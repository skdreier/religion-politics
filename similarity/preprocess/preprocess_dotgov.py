# preprocess_dotgov.py

import common.disable_warnings
import common.configure_logging

import argparse
import h5py
import logging
import numpy as np
import os
import sqlite3
import spacy

from common.spacy_model import load_default_model
from documents.load import load_dotgov_files
from documents.store import TextStore
from vectors.store import VectorStore


BATCH_SIZE = 2500
MIN_SENT_TOKS = 4
N_THREADS = 8


def process(texts, model, tstore, vstore):
    output = model.pipe(texts, as_tuples=True,
                        n_threads=N_THREADS, batch_size=BATCH_SIZE)

    for doc, meta in output:
        sents = []
        vecs = []

        for sent in doc.sents:
            if sent.end - sent.start > MIN_SENT_TOKS:
                vec = sent.vector
                norm = np.linalg.norm(vec)

                if norm >= 1e-8:
                    # (there's no point in storing a zero vector or searching
                    # against it...)
                    vecs.append(vec / norm)
                    sents.append(sent.text)

        n_sents = len(sents)
        if n_sents == 0:
            # nothing to do here
            continue

        doc_idx = tstore.write_idx  # keep this to update vstore pointers below
        tstore.write(sents, vstore.write_idx, meta)
        vstore.write(vecs, doc_idx)

    tstore.reconcile()
    vstore.reconcile()
    logging.info('Total: {} documents, {} vectors'.format(
                  tstore.write_idx, vstore.write_idx))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_dir')
    ap.add_argument('output_prefix')
    args = ap.parse_args()

    h5_path = '{}.h5'.format(args.output_prefix)
    sql_path = '{}.sqlite'.format(args.output_prefix)

    logging.info('Starting...')

    model = load_default_model()
    logging.info('Model loaded!')

    texts = load_dotgov_files(args.input_dir)
    sql_conn = None
    try:
        sql_conn = sqlite3.connect(sql_path)
        tstore = TextStore(sql_conn)

        with h5py.File(h5_path, 'a') as h5f:
            vstore = VectorStore(h5f)
            process(texts, model, tstore, vstore)

    finally:
        if sql_conn:
            sql_conn.close()

    logging.info('Done!')


if __name__ == '__main__':
    main()
