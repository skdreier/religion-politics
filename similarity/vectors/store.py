# vector.store

import common.disable_warnings

import h5py
import logging
import numpy as np


BUFFER_SIZE = 100000
CHUNK_SIZE = 2500

VEC_DS_INFO = {
    'name': 'vector',
    'hdim': 300,
    'dtype': np.float32,

    # this speeds things up a bunch, and we don't gain a lot by
    # compressing word vectors anyways
    'compression': None
}

VEC_MAP_INFO = {
    'name': 'vec2text',  # ugh
    'hdim': 0,
    'dtype': np.dtype([ ('text_idx', np.uint64), ('offset', np.uint64) ]),
    'compression': 'lzf'
}


class VectorStore:
    def __init__(self, h5f):
        self.h5f = h5f

        self.vec_ds, self.write_idx, self.size = \
                self._load_data(**VEC_DS_INFO)

        self.map_ds, map_idx, map_size = \
                self._load_data(**VEC_MAP_INFO)

        # we're just going to use vec_idx and vec_size from here on
        # out, so make sure these are the same now
        assert self.write_idx == map_idx, \
               'vector and map indices are different ({}, {})'.format(
                self.write_idx, map_idx
               )
        assert self.size == map_size, \
               'vector and map sizes are different ({}, {})'.format(
                self.size, map_size
               )

    def get_sent_coords(self, vec_idxs):
        coords = np.zeros((vec_idxs.shape[0], vec_idxs.shape[1]),
                          dtype=VEC_MAP_INFO['dtype'])

        # rather than use h5py's fancy indexing (which requires sorted indices),
        # just do it the good ol' fashioned way -- we shouldn't be doing this
        # more than once anyways -- reopt later if needed
        for ptr, vec_idx in np.ndenumerate(vec_idxs):
            coords[ptr] = self.map_ds[vec_idx]

        return coords


    def reconcile(self):
        # probably should figure out open/close semantics instead, oops
        self.vec_ds.attrs['n_entries'] = self.write_idx
        self.map_ds.attrs['n_entries'] = self.write_idx
        self.h5f.flush()

    def write(self, vecs, doc_idx):
        n_vecs = len(vecs)
        vec_idx = self.write_idx
        vec_idx_next = vec_idx + n_vecs

        if vec_idx_next > self.size:
            self._resize(vec_idx_next)

        self.vec_ds[vec_idx:vec_idx_next] = vecs
        self.map_ds[vec_idx:vec_idx_next] = [
                (doc_idx, v_idx) for v_idx in range(n_vecs)]

        self.write_idx = vec_idx_next

    def _load_data(self, name, hdim, dtype, compression):
        # logging.info('Loading {} data...'.format(name))

        try:
            dataset = self.h5f[name]
            n_entries = dataset.attrs['n_entries']

            if hdim == 0:
                size = dataset.size
            else:
                # h5py reports 2d arrays' size as if all the entries were
                # concatenated
                size = dataset.size // hdim

        except KeyError:
            if hdim == 0:
                shape = (BUFFER_SIZE, )
                maxshape = (None, )
                chunk = (CHUNK_SIZE, )
            else:
                shape = (BUFFER_SIZE, hdim)
                maxshape = (None, hdim)
                chunk = (CHUNK_SIZE, hdim)

            dataset = self.h5f.create_dataset(name, shape,
                    dtype=dtype, chunks=chunk, maxshape=maxshape,
                    compression=compression, shuffle=False)

            n_entries = 0
            size = shape[0]

        return dataset, n_entries, size

    def _resize(self, vec_idx_next):
        while (self.size < vec_idx_next):
            self.size += 3*BUFFER_SIZE

        # logging.info('Resizing vector store to {}'.format(vec_size))
        self.vec_ds.resize(self.size, axis=0)
        self.map_ds.resize(self.size, axis=0)
        self.h5f.flush()

