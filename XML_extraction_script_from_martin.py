from xml.dom.minidom import parseString

input_text = '''
   <paragraph>Statestream is an experimental toolbox for <link destination="https://arxiv.org/abs/1806.04965">streaming</link> (see also <link destination="docs/from_one_frame_to_the_next.md">this explanation</link>) deep neural networks. It provides tools to easily design, train, visualize, and manipulate streaming deep neural networks.</paragraph>
''' 
input_text_1 = '''
<paragraph><link destination="https://wiki.ubuntuusers.de/Xfce_Installation/">Xfce</link> Desktop environment. Please see the <link destination="docs/troubleshooting.md">troubleshooting section</link> for color problems.</paragraph>
'''

# '<paragraph>Thomas Müller: <link url="https://somedomain">click here</link> to download file</paragraph>'

input_text = input_text.replace('\n', '')
input_text = ' '.join(input_text.split())
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
            if node.nodeValue != ' ':
                print(f'Text: "{node.nodeValue}"')



