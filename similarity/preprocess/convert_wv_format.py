# convert_wv_format.py

import common.disable_warnings
import common.configure_logging

import argparse
import logging
import numpy as np
import os

from common.utils import pbar_line_generator
from spacy.vocab import Vocab


VEC_HDIM = 300  # woo magic


def load_vectors_into_model(input_path, model):
    # paragram-300-SL999 needs latin-1,
    # a fact that i sadly rediscover every few months
    for line in pbar_line_generator(input_path, encoding='latin-1'):
        toks = line.split(' ')
        if len(toks) < VEC_HDIM + 1: continue

        word = ' '.join(toks[ :-VEC_HDIM])  # unlikely, but just in case
        vector = np.array(toks[-VEC_HDIM: ], dtype=np.float32)
        model.set_vector(word, vector)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_path')
    ap.add_argument('output_path')
    ap.add_argument('--append', action='store_true')
    args = ap.parse_args()

    if args.append:
        logging.info('Loading existing model...')
        model = Vocab().from_disk(args.output_path)
    else:
        model = Vocab()

    logging.info('Loading vectors into spacy...')
    load_vectors_into_model(args.input_path, model)

    logging.info('Writing model to disk...')
    model.to_disk(args.output_path)

    logging.info('Done!')


if __name__ == '__main__':
    main()
