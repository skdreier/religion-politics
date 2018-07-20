"""
Author: Sofia Serrano
"""

import re


@outputSchema("document:chararray")
def converttochararray(text):
    # if the entire document is < <length_threshold> chars long, it's not going to have useful cooccurrences
    # anyway
    length_threshold = 5
    try:
        text = text.decode('utf-8')
    except:
        try:
            text = str(text).strip()
        except:
            return ''
    if text == 'None' or len(text) < length_threshold:
        return ''
    else:
        return text.lower()