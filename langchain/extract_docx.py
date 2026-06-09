import zipfile
import re
from pathlib import Path

docx_path = Path(r"c:\Users\EDY\Desktop\LLMops题目.docx")
out_path = Path(r"d:\dm\langchain\LLMops题目.txt")

with zipfile.ZipFile(docx_path) as z:
    xml = z.read("word/document.xml").decode("utf-8")

text = re.sub(r"<w:tab/>", "\t", xml)
text = re.sub(r"</w:p>", "\n", text)
text = re.sub(r"<[^>]+>", "", text)

lines = [line.strip() for line in text.splitlines() if line.strip()]
out_path.write_text("\n".join(f"{i}. {line}" for i, line in enumerate(lines, 1)), encoding="utf-8")
print(f"Wrote {len(lines)} lines to {out_path}")
