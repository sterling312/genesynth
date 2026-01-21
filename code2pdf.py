import glob
import logging
from itertools import chain
from PyPDF2 import PdfWriter, PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black
from reportlab.lib import colors

logger = logging.getLogger(__name__)

GITHUB = {
    "bg": colors.HexColor("#f6f8fa"),
    "border": colors.HexColor("#d0d7de"),
    "text": colors.HexColor("#24292f"),
    "lineno": colors.HexColor("#57606a"),
}

def fetch_pages(glober='*.pdf'):
    filenames = glob.glob(glober)
    for filename in filenames:
        reader = PdfReader(filename)
        for page in reader.pages:
            yield page

def code_finder(basedir: str, output: str = 'output.pdf'):
    logger.info(f'basedir {basedir}')
    writer = PdfWriter()
    for filename in chain(glob.glob(f'{basedir}/*.py'), glob.glob(f'{basedir}/**/*.py')):
        logger.info(f'reading {filename}')
        code = open(filename, 'rb').read()
        filepath = filename.replace(f'{basedir}/', '')
        render_code_pdf(output, code, filepath)
        for page in fetch_pages(output):
            writer.add_page(page)
    with open(output, "wb") as fp:
        writer.write(fp)

def render_code_pdf(output_path: str, code: str, filepath: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    code_style = ParagraphStyle(
        name="GitHubCode",
        fontName="Courier",
        fontSize=9,
        leading=13,
        textColor=GITHUB["text"],
        alignment=TA_LEFT,
        leftIndent=6,
        rightIndent=6,
        spaceBefore=6,
        spaceAfter=6,
    )

    story = []

    story.append(Paragraph(filepath, title_style))
    story.append(Spacer(1, 12))

    numbered_code = "\n".join(page_wrap(i, line) for i, line in enumerate(code.splitlines(), start=1))

    story.append(Preformatted(numbered_code, code_style))

    doc.build(story)

def page_wrap(i, line):
    line = line.decode('utf-8')
    if len(line) < 80:
        return f"{i:4d}  {line}"
    else:
        wrap = '\n'.join(f"{' '*4} {line[i*80:(i+1)*80]}" for i in range(1, len(line) % 80))
        return f"{i:4d}  {line[:80]}\n{wrap}"

if __name__ == '__main__': 
    import sys
    logging.basicConfig(level='INFO')
    code_finder(*sys.argv[1:])
