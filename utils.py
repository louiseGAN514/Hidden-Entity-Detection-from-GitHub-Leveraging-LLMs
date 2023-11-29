from bs4 import BeautifulSoup
from xml.dom.minidom import parseString
from pprint import pprint


# EXTRact link, text, previous text and next text from hyperlink strings
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


# extract paragraph containing hyperlinks
def para_extraction_with_links(xml_str):
    soup = BeautifulSoup(xml_str, features='lxml-xml')
    try:
        link, text, context, raw_context = [], [], [], []
        for _match in soup.find_all('paragraph'):
            if '<link destination' in str(_match) and 'http' in str(_match):
                p_text = _match.get_text()
                hyperlinks = _match.find_all('link')
                for _link in hyperlinks:
                    l_text = _link.get_text()
                    l_url = _link['destination']
                    link.append(l_url)
                    text.append(l_text)
                    context.append(p_text)
                    raw_context.append(str(_match))
        return link, text, context, raw_context
    except Exception as e:
        raise e

# link_str = "<link destination=\"http://pandas.pydata.org/\">pandas</link>"
# print(hyperlink_extraction(link_str))


# extract paragraph containing hyperlinks
def para_extraction_with_links_XML_parser(xml_str):
    soup = BeautifulSoup(xml_str, features='lxml-xml')
    try:
        context, links = [], []
        for _match in soup.find_all('paragraph'):
            if '<link destination' in str(_match) and 'http' in str(_match):
                _context, _links = xml_parser_from_martin(str(_match))
                context.append(_context)
                links.append(_links)
        return context, links
    except Exception as e:
        raise e



def xml_parser_from_martin(input_text):
    print('Input text:\n', input_text)
    dom = parseString(input_text)
    root = dom.firstChild
    context, links = '', []
    for node in root.childNodes:
        match node.nodeType:
            case node.ELEMENT_NODE:
                if node.tagName == "link":
                    try:
                        link_text = node.firstChild.nodeValue
                        link_text = link_text.strip()
                        # for i in range(node.attributes.length):
                        #     print(node.attributes.item(i).nodeName, node.attributes.item(i).nodeValue)
                        urls = [node.attributes.item(i).nodeValue.strip()
                            for i in range(node.attributes.length)
                            if node.attributes.item(i).nodeName == "destination"]
                        if len(context) > 0 and len(link_text) > 0:
                            _text_start, _text_end = len(context)+1, len(context)+1+len(link_text)
                            context = context + ' ' + link_text
                        elif len(context) == 0 and len(link_text) > 0:
                            _text_start, _text_end = len(context), len(context)+len(link_text)
                            context = link_text
                        else:
                            _text_start, _text_end = 0, 0

                        _url_start, _url_end = len(context)+1, len(context)+1+len(urls[0])
                        context = context + ' ' + urls[0]
                        links.append({'text_start': _text_start, 'text_end':_text_end, 'url_start':_url_start, 'url_end':_url_end})
                        # print(f'Link: "{link_text}" {urls[0]}')
                    except AttributeError as e:
                        pass
            case node.TEXT_NODE:
                if node.nodeValue != ' ':
                    context = context + ' ' + node.nodeValue
                    context = context.strip()
                    # print(f'Text: "{node.nodeValue}"')
    print('Context: ', context)
    print('Links: ')
    pprint(links)
    for link in links:
        print(context[link['text_start']:link['text_end']])
        print(context[link['url_start']:link['url_end']])
    return context, links


