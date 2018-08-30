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
    python -m preprocess.preprocess_dotgov \
        /m-pinotHD/lucylin/dotgov/arcs/bucket-0 \
        /m-pinotHD/nobackup/lucylin/dotgov-compiled/arcs-0
    ```

3. get similarity for a set of queries, across all buckets (output written to
    `output/matches.json` and `output/matches.xlsx`):
    ```
    python find_matches.py \
        /m-pinotHD/nobackup/lucylin/dotgov-compiled \
        ./queries \
        /m-pinotHD/nobackup/lucylin/output
    ```

4. postprocessing:
    a. computing per-query ratios of Democrats/Republican/etc sites:
    ```
    python -m postprocess.compute_party_ratios \
        /m-pinotHD/nobackup/lucylin/output/matches.json \
        /m-pinotHD/nobackup/lucylin/output
    ```

    b. conversion to tsv (e.g., for use on the cluster):
    ```
    python -m postprocess.matches_to_csv \
        /m-pinotHD/nobackup/lucylin/output/matches.json \
        /m-pinotHD/nobackup/lucylin/output/matches.tsv
    ```

    c. intersection of documents w/religious keywords and documents w/
        policy matches:
    ```
    python -m postprocess.intersect_religion_docs \
        /m-pinotHD/sofias6/dotgov/all_religious_captures_urls/ \
        /m-pinotHD/nobackup/lucylin/output/matches.json
        /m-pinotHD/nobackup/lucylin/relpol-intersect-output/
    ```

