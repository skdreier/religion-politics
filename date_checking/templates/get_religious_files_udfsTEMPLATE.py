@outputSchema("document:chararray")
def pad_string(document):
    # if the entire document is < <length_threshold> chars long, it's not going to have useful cooccurrences
    # anyway
    try:
        document = document.decode('utf-8')
    except:
        document = str(document)
    document = " " + document + " "
    return document.lower()
