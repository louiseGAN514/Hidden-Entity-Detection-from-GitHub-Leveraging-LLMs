from bs4 import BeautifulSoup


# extract link, text, previous text and next text from hyperlink strings
def hyperlink_extraction(hl_str):
    soup = BeautifulSoup(hl_str, features='lxml-xml')
    matches = soup.find_all('link')
    if len(list(matches)) < 1:
        return None, None, None, None
    elif len(list(matches)) == 1:
        for _match in matches:
            link = _match.attrs['destination']
            text = _match.text
            prev_text = _match.previousSibling
            next_text = _match.nextSibling
        return link, text, prev_text, next_text
    else:
        link, text, prev_text, next_text = [], [], [], []
        for _match in matches:
            link.append(_match.attrs['destination'])
            text.append(_match.text)
            prev_text.append(_match.previousSibling)
            next_text.append(_match.nextSibling)
        return link, text, prev_text, next_text


# link_str = "<link destination=\"http://pandas.pydata.org/\">pandas</link>"
# print(hyperlink_extraction(link_str))
