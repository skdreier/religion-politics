# common.spacy_model

import common.disable_warnings
import spacy

from spacy.language import Language

# getting around the fact that these don't install properly on conda...
# MODEL_PATH = '/homes/gws/lucylin/Packages/spacy/en_core_web_lg-2.0.0'
# ... or just use the paraphrastic vectors instead
MODEL_PATH = '/m-pinotHD/nobackup/lucylin/paragram/compiled'


def load_default_model():
    # model = spacy.load(MODEL_PATH, disable=['tagger', 'parser', 'ner'])
    vocab = spacy.vocab.Vocab().from_disk(MODEL_PATH)
    model = Language(vocab)

    # ideally, we'd use their parser to do sentence segmentation,
    # but we don't have all day (week/month), so fall back to the basic version
    sbd = model.create_pipe('sentencizer')
    model.add_pipe(sbd)

    return model

