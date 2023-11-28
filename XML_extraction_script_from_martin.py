from xml.dom.minidom import parseString

input_text = '''
   <paragraph>This repository contains code and data used in the following <link destination="https://arxiv.org/abs/1806.04330">paper</link>:</paragraph>
   <textblock>@inproceedings{lan2018toolkit,
  author     = {Lan, Wuwei and Xu, Wei},
  title      = {Neural Network Models for Paraphrase Identification, Semantic Textual Similarity, Natural Language Inference, and Question Answering},
  booktitle  = {Proceedings of COLING 2018},
  year       = {2018}
} 
</textblock>'''

# '<paragraph>Thomas Müller: <link url="https://somedomain">click here</link> to download file</paragraph>'

input_text = input_text.replace('\n', '')
print(input_text)
dom = parseString(input_text)
root = dom.firstChild

for node in root.childNodes:
    match node.nodeType:
        case node.ELEMENT_NODE:
            if node.tagName == "link":
                link_text = node.firstChild.nodeValue
                urls = [(node.attributes.item(i).nodeName, node.attributes.item(i).nodeValue)
                        for i in range(node.attributes.length)
                        if node.attributes.item(i).nodeName == "url"]
                print(f'Link: "{link_text}" {urls}')
        case node.TEXT_NODE:
            print(f'Text: "{node.nodeValue}"')



