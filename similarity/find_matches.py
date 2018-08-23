# find_matches.py

import common.disable_warnings
import common.configure_logging

import argparse
import glob
import h5py
import heapq
import itertools
import json
import logging
import numpy as np
import os
import sqlite3

from openpyxl import Workbook
from operator import itemgetter
from tqdm import tqdm

from common.spacy_model import load_default_model
from documents.load import load_query_files
from documents.store import TextStore
from vectors.similarity import get_most_similar
from vectors.store import VectorStore


def load_queries(query_dir):
    model = load_default_model()
    query_info = load_query_files(query_dir)
    strs, ids = zip(*query_info)
    strs = list(strs)

    # precompute a vector per query
    sents = model.pipe(strs, batch_size=100)
    vecs = np.array([s.vector / np.linalg.norm(s.vector) for s in sents])

    del model
    return strs, vecs, list(ids)


def search(query_vecs, corpus_dir, output_dir, n_best):
    h5_paths = sorted(glob.glob(os.path.join(corpus_dir, '*.h5')))
    n_queries = query_vecs.shape[0]
    matches = [[] for _ in range(n_queries)]
    sort_kwargs = {'key': itemgetter('score'), 'reverse': True}

    for h5_path in h5_paths:
        # in theory, we could parallelize searching across buckets, but np
        # multithreads under the covers, so we'd basically be stealing cores
        # for ourselves...
        base_path = os.path.splitext(h5_path)[0]
        filename = os.path.basename(base_path)
        logging.info('Searching {}...'.format(filename))

        sql_path = '{}.sqlite'.format(base_path)
        chkpt_path = os.path.join(output_dir,
                                  'checkpoint-{}.npz'.format(filename))

        sub_matches = _match_bucket(query_vecs, h5_path, sql_path,
                                    chkpt_path, n_best)

        for q_idx, q_matches in enumerate(sub_matches):
            q_matches.sort(**sort_kwargs)
            existing = matches[q_idx]
            merged = heapq.merge(existing, q_matches, **sort_kwargs)
            matches[q_idx] = list(itertools.islice(merged, n_best))

    return matches


def _match_bucket(query_vecs, h5_path, sql_path, chkpt_path, n_best):
    sql_conn = None

    with h5py.File(h5_path, 'r') as h5f:
        vstore = VectorStore(h5f)
        scores, sent_coords = get_most_similar(vstore, query_vecs,
                                               chkpt_path, n_best)
    try:
        sql_conn = sqlite3.connect(sql_path)
        tstore = TextStore(sql_conn)

        logging.info('Updating found matches...')
        matches = _collate_matches(tstore, scores, sent_coords, n_best)

    finally:
        if sql_conn: sql_conn.close()

    return matches


def _collate_matches(tstore, scores, sent_coords, n_best):
    n_queries = scores.shape[1]

    all_matches = []
    with tqdm(total=n_best*n_queries) as pbar:
        # queries are by column, unfortunately
        for q_scores, q_coords in zip(scores.T, sent_coords.T):
            q_info = tstore.get_sent_info(q_coords)

            matches = []
            for s_score, s_info in zip(q_scores, q_info):
                s_info['score'] = str(s_score)
                matches.append(s_info)
                pbar.update()

            all_matches.append(matches)

    return all_matches


def write_json(json_path, queries, query_ids, matches):
    qms = [{'id': qid, 'query': q, 'matches': ms}
            for qid, q, ms in zip(query_ids, queries, matches)]

    with open(json_path, 'w') as f:
        json.dump(qms, f)


def write_spreadsheet(wb_path, queries, query_ids, matches):
    wb = Workbook()
    ws = wb.active

    for qid, query, matches in zip(query_ids, queries, matches):
        ws.title = qid
        ws.append(['# query: {}'.format(query)])

        header = ['score', 'sentence', 'url', 'checksum', 'date']
        ws.append(header)
        for m in matches:
            ws.append(m[k] for k in header)

        ws = wb.create_sheet()

    wb.save(wb_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('corpus_dir')
    ap.add_argument('query_dir')
    ap.add_argument('output_dir')
    ap.add_argument('-n', dest='n_best', default=500)
    args = ap.parse_args()

    logging.info('Starting...')

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    logging.info('Loading queries...')
    query_strs, query_vecs, query_ids = load_queries(args.query_dir)

    logging.info('Finding matches...')
    matches = search(query_vecs, args.corpus_dir, args.output_dir, args.n_best)

    # write this two ways -- once for my convenience, once for others'
    logging.info('Writing output...')

    json_path = os.path.join(args.output_dir, 'matches.json')
    write_json(json_path, query_strs, query_ids, matches)

    wb_path = os.path.join(args.output_dir, 'matches.xlsx')
    write_spreadsheet(wb_path, query_strs, query_ids, matches)

    logging.info('Done!')


if __name__ == '__main__':
    main()
