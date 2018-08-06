

@outputSchema("date:chararray")
def pad_to_correct_length(date):
    # if the entire document is < <length_threshold> chars long, it's not going to have useful cooccurrences
    # anyway
    try:
        date = date.decode('utf-8').strip()
    except:
        date = str(date).strip()
    date = date[:14]
    if len(date) < 14:
        return date + '0' * (14 - len(date))
    else:
        return date