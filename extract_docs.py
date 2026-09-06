import os
import zipfile
import xml.etree.ElementTree as ET

def get_docx_text(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            texts = [node.text for node in tree.iter() if node.text]
            return ' '.join(texts)
    except Exception as e:
        return str(e)

base = r'c:\Users\USER\Desktop\პორთფოლი 2020დან\აქტივობები'
output_lines = []

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.docx'):
            p = os.path.join(root, f)
            folder_name = os.path.basename(os.path.dirname(p))
            text = get_docx_text(p)
            output_lines.append(f"Folder: {folder_name} | File: {f}")
            output_lines.append(text)
            output_lines.append("-" * 50)

with open('extracted_texts.txt', 'w', encoding='utf-8') as out:
    out.write("\n".join(output_lines))

print("Extracted text saved to extracted_texts.txt")
