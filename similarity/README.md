# README

warning: discovering the various locations of lazily hard-coded paths is mostly
left as an exercise to the reader.

1. requirements:
    * python 3.6 (ish) and packages: h5py, openpyxl, spacy, tqdm,
        numpy (1.15 or greater; install after spacy, which uses an older
        version)

    * a spacy model with word vectors, like `en_core_web_lg`
        (note: fix the hard-coded path in `documents/spacy_model.py`),
        or compile one via `preprocess/convert_wv_format.py`

    * a copy of the senate/house data (please contact us for how to access
        that)

2. preprocess raw-ish dotgov data (downloaded from the cluster) per bucket,
   e.g.:
    ```
    python -m preprocess.preprocess_dotgov \
        ${DATA_DIR}/dotgov/arcs/bucket-0/ \
        ${SOME_OTHER_DIR}/dotgov-compiled/arcs-0
    ```

3. get similarity for a set of queries, across all buckets (output written to
    `output/matches.json` and `output/matches.xlsx`):
    ```
    python ./find_matches.py \
        ${SOME_OTHER_DIR}/dotgov-compiled/ \
        ./queries/ \
        ${OUTPUT_DIR}
    ```

4. postprocessing:

    a. annotate the matched output with the document's party affiliation and
       if the document also contains religious matches:
    ```
    python -m postprocess.annotate \
        ${OUTPUT_DIR}/matches.json \
        ${OUTPUT_DIR}/annotated
    ```

    b. conversion to tsv (e.g., for use on the cluster):
    ```
    python -m postprocess.matches_to_csv \
        ${OUTPUT_DIR}/matches.json \
        ${OUTPUT_DIR}/matches.tsv
    ```
