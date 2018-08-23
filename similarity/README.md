# README

(more personal reminder than actual documentation... --lucy)

1. requirements:
    * python 3.6 (ish) and packages: h5py, openpyxl, spacy, tqdm,
        numpy (1.15 or greater; install after spacy, which uses an older
        version)

    * a spacy model with word vectors, like `en_core_web_lg`
        (note: fix the hard-coded path in `documents/spacy_model.py`),
        or compile one via `convert_wv_format.py`

2. preprocess raw-ish dotgov data (from the cluster) per bucket, e.g.:
    ```
    python preprocess_dotgov.py \
        /m-pinotHD/lucylin/dotgov/arcs/bucket-0 \
        /m-pinotHD/nobackup/lucylin/arcs/bucket-0
    ```

3. get similarity for a set of queries, across all buckets (output written to
    `output/matches.json` and `output/matches.xlsx`):
    ```
    python find_matches.py \
        /m-pinotHD/nobackup/lucylin/arcs \
        ./queries \
        ./output
    ```
