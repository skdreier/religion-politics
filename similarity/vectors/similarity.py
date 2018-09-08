# vectors.similarity

import common.configure_logging
import common.disable_warnings

import logging
import numpy as np
from tqdm import tqdm


BATCH_SIZE = 25000
CHECKPOINT_TIME = 50*BATCH_SIZE


def get_most_similar(vstore, query_vecs, chkpt_path, n_best):
    vec_ds = vstore.vec_ds
    n_entries = vstore.size
    n_queries = query_vecs.shape[0]

    # the bottom N_BEST entries are from previous iterations,
    # and the rest is working memory
    scores = np.zeros((BATCH_SIZE + n_best, n_queries), dtype=np.float32)
    indices = np.zeros((BATCH_SIZE + n_best, n_queries), dtype=np.uint64)

    next_chkpt = CHECKPOINT_TIME

    for idx in tqdm(range(0, n_entries, BATCH_SIZE)):
        if idx + BATCH_SIZE > n_entries:
            idx_next = n_entries
            batch_size = n_entries - idx

            # make sure we don't accidentally include these
            scores[batch_size:BATCH_SIZE] = -1
            indices[batch_size:BATCH_SIZE] = 0
        else:
            idx_next = idx + BATCH_SIZE
            batch_size = BATCH_SIZE

        batch = vec_ds[idx:idx_next]

        scores[ :batch_size] = batch.dot(query_vecs.T)
        indices[ :batch_size] = np.mgrid[idx:idx_next, 0:n_queries][0]

        best_entries = np.argpartition(scores, -n_best, axis=0)[-n_best: ]
        scores[-n_best: ] = np.take_along_axis(scores, best_entries, axis=0)
        indices[-n_best: ] = np.take_along_axis(indices, best_entries, axis=0)

        if idx > next_chkpt:
            _write_chkpt(chkpt_path, idx, scores, indices, n_best)
            next_chkpt += CHECKPOINT_TIME

    _write_chkpt(chkpt_path, idx, scores, indices, n_best)
    sent_coords = vstore.get_sent_coords(indices[-n_best: ])

    return scores[-n_best: ], sent_coords


def _write_chkpt(path, curr_idx, scores, indices, n_best):
    with open(path, 'wb') as f:
        np.savez_compressed(path, curr_idx=curr_idx, scores=scores[-n_best: ],
                            indices=indices[-n_best: ])
