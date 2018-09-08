@outputSchema("content:chararray")
def lowercase_and_add_space_bookends(text):
    try:
        text = text.decode('utf-8')
    except:
        try:
            text = str(text).strip()
        except:
            return ''
    return ' ' + text.lower() + ' '
