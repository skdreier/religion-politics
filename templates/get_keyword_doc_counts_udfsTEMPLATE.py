"""
Author: Sofia Serrano
"""


import re


complete_regex = re.compile(INSERTALLREGEXESHERE)

simplified_words = [
    STARTLINEREPEAT
    'INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES'
    ENDLINEREPEAT
]

output_schema = "allwords:tuple("
for i in range(len(simplified_words) - 1):
    word = simplified_words[i]
    output_schema += word + ":int,"
output_schema += simplified_words[-1] + ":int)"

@outputSchema(output_schema)
def getindicatorvars(text):
    found_words = {}
    words_found = complete_regex.findall(text)
    for word in words_found:
        found_words[word] = 1
    return \
        STARTLINEREPEAT
        found_words.get(INSERTTERMHERE, 0)
        ENDLINEREPEAT


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