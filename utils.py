from bs4 import BeautifulSoup
import json
from xml.dom.minidom import parseString
from pprint import pprint


# match a URL string pair, return the match score in [0, 1]
# 1 represents exact match, 0 represents no overlapping match
from difflib import SequenceMatcher

def longest_common_substring(s1: str, s2: str) -> str:
    """Computes the longest common substring of s1 and s2"""
    seq_matcher = SequenceMatcher(isjunk=None, a=s1, b=s2)
    match = seq_matcher.find_longest_match(0, len(s1), 0, len(s2))
    # print('Point: 9')
    if match.size:
        return s1[match.a : match.a + match.size]
    else:
        return ""

def partial_match(s1 : str, s2 : str) -> float:
    """Computes the longest common substring percentage of s1 and s2 on s2"""
    # assert min(len(s1), len(s2)) > 0, "One of the given string is empty"
    # print(longest_common_substring(s1, s2))
    return len(longest_common_substring(s1, s2))/len(s2)


def parse_answer(ans_str):
    if '[INST]' in ans_str.strip()[:6]:
        ans_str = ans_str.strip()[6:].strip()
    if 'NST]' in ans_str.strip()[:4]:
        ans_str = ans_str.strip()[4:].strip()
    if 'Note:' in ans_str.strip():
        ans_str = ans_str.strip().split('Note:')[0].strip()
    if '# Explanation' in ans_str.strip():
        ans_str = ans_str.strip().split('# Explanation')[0].strip()


    ans_str = ans_str.strip()
    ans_str = ' '.join(ans_str.split())
    # print(ans_str)
    if 'input:' in ans_str:
        ans_str = ans_str.strip().split('input:')[-1]
    elif 'the input text:' in ans_str:
        ans_str = ans_str.strip().split('the input text:')[-1]
    elif 'the annotated URLs:' in ans_str:
        ans_str = ans_str.strip().split('the annotated URLs:')[-1]
    elif 'the input URL:' in ans_str:
        ans_str = ans_str.strip().split('the input URL:')[-1]
    elif 'the input source:' in ans_str:
        ans_str = ans_str.strip().split('the input source:')[-1]
    elif 'the input URLs:' in ans_str:
        ans_str = ans_str.strip().split('the input URLs:')[-1]
    elif 'the given URL:' in ans_str:
        ans_str = ans_str.strip().split('the given URL:')[-1]
    elif 'the given URLs:' in ans_str:
        ans_str = ans_str.strip().split('the given URLs:')[-1]
    elif 'the URLs you provided:' in ans_str:
        ans_str = ans_str.strip().split('the URLs you provided:')[-1]
    elif 'Output:' in ans_str:
        ans_str = ans_str.strip().split('Output:')[-1]
    elif 'output:' in ans_str:
        ans_str = ans_str.strip().split('output:')[-1]
    elif 'put:' in ans_str:
        ans_str = ans_str.strip().split('put:')[-1]
    elif 'labels:' in ans_str:
        ans_str = ans_str.strip().split('labels:')[-1].strip()
    #ans_str = [split for split in ans_str if split != '']
    if 'Output:' in ans_str:
        ans_str = ans_str.strip().split('Output:')[-1] 
     
    if '[{' in ans_str:
        if '}]' in ans_str:
            ans_str = ans_str.split('}]')[0] + '}]'
        elif '} ]' in ans_str:
            ans_str = ans_str.split('} ]')[0] + '}]'
        elif '}' in ans_str:
            ans_str = ans_str.split('}')[0] + '}]'
        if '*' in ans_str:
            ans_str = ans_str.split('*')[-1]
        ans_str = ans_str.strip()
        try:
            ans_str = ans_str.replace("\'", "\"")
            ans_str = ans_str.replace("\\_", "_").replace(', ', ',')
            ans_str = json.loads(ans_str)
        except Exception as e:
            # print(ans_str)
            # traceback.print_exc()
            print(e)
    elif '[ {' in ans_str:
        ans_str = ans_str.replace('[ {', '[{')
        ans_str = ans_str.split('} ]')[0] + '}]'
        if '*' in ans_str:
            ans_str = ans_str.split('*')[-1]
        ans_str = ans_str.strip()
        try:
            ans_str = ans_str.replace("\'", "\"") 
            ans_str = ans_str.replace("\\_", "_").replace(', ', ',')
            ans_str = json.loads(ans_str)
        except Exception as e:
            # print(ans_str)
            # traceback.print_exc()
            print(e)
    elif '}]' in ans_str:
        if ans_str[0] == '{':
            ans_str = '[' + ans_str
        elif ans_str[0] == 'U' and ans_str[3] == "'":
            ans_str = "[{'" + ans_str
        elif ans_str[0] == 'U' and ans_str[3] == '"':
            ans_str = '"' + ans_str
            ans_str = "[{" + ans_str
        elif ans_str[:3] == 'ttp' and "'label'" in ans_str:
            ans_str = "[{'URL': 'h" + ans_str
        elif ans_str[:3] == 'ttp' and '"label"' in ans_str:
            ans_str = '[{"URL": "h' + ans_str
        elif ans_str[0] == ':' and "'label'" in ans_str:
            ans_str = "[{'URL'" + ans_str
        elif ans_str[0] == ':' and '"label"' in ans_str:
            ans_str = '[{"URL"' + ans_str
        try:
            ans_str = ans_str.replace("\'", "\"") 
            # ans_str = r"{}".format(ans_str)
            ans_str = ans_str.replace("\\_", "_").replace(', ', ',')
            ans_str = json.loads(ans_str)
        except Exception as e:
            print('error point 0')
            print(e)
    elif '} ]' in ans_str:
        if ans_str[0] == '{':
            ans_str = '[' + ans_str
        elif ans_str[0] == 'U' and ans_str[3] == "'":
            ans_str = "[{'" + ans_str
        elif ans_str[0] == 'U' and ans_str[3] == '"':
            ans_str = '"' + ans_str
            ans_str = "[{" + ans_str
        elif ans_str[:3] == 'ttp' and "'label'" in ans_str:
            ans_str = "[{'URL': 'h" + ans_str
        elif ans_str[:3] == 'ttp' and '"label"' in ans_str:
            ans_str = '[{"URL": "h' + ans_str
        elif ans_str[0] == ':' and "'label'" in ans_str:
            ans_str = "[{'URL'" + ans_str
        elif ans_str[0] == ':' and '"label"' in ans_str:
            ans_str = '[{"URL"' + ans_str
        try:
            ans_str = ans_str.replace("\'", "\"") 
            # ans_str = r"{}".format(ans_str)
            ans_str = ans_str.replace("\\_", "_").replace(', ', ',')
            ans_str = json.loads(ans_str)
        except Exception as e:
            print('error point 00')
            print(e)
    elif '} {' in ans_str:
        ans_str = ans_str.replace('} {', '}, {')
        ans_str = '[' + ans_str + ']'
        try:
            ans_str = ans_str.replace("\'", "\"") 
            # ans_str = r"{}".format(ans_str)
            ans_str = json.loads(ans_str)
        except Exception as e:
            print('error point 1')
            print(ans_str)
            print(e)

    else:
        try:
            # ans_str = ans_str.replace("\'", "\"") 
            ans_str = json.loads(ans_str)
        except Exception as e:
            print(e)

    # if '*' in ans_str: 
        # print(ans_str)
    return ans_str



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


