#!/usr/bin/env python3
"""Rebuild the two PDFs from this repository's Markdown; no network access needed.

Build environment used: Python 3.13, WeasyPrint 68.0, markdown-it-py 4.2.0.
Install those Python packages and WeasyPrint's native requirements in a separate
virtual environment. This script only writes the two files under pdf/.
No font files are bundled; the system needs DejaVu Sans and DejaVu Sans Mono.
"""
from pathlib import Path
import html
import re
from markdown_it import MarkdownIt
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
MD = MarkdownIt('commonmark', {'html': False}).enable('table')
CSS = r'''
@page {
  size: A4;
  margin: 19mm 17mm 20mm;
  @top-left { content: "TOMSEC  /  CLASSROOM EDITION"; font: 7.4pt "DejaVu Sans"; letter-spacing: 1.1pt; color: #526577; }
  @bottom-left { content: "EDITION 1.1  |  17 SEPTEMBER 2026"; font: 7pt "DejaVu Sans"; color: #687787; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.5pt "DejaVu Sans"; color: #23394a; }
}
@page:first {
  margin: 0;
  @top-left { content: none; }
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}
* { box-sizing: border-box; }
html { font-family: "DejaVu Sans", sans-serif; color: #203448; font-size: 9.6pt; }
body { margin: 0; line-height: 1.48; }
p { margin: 0 0 7pt; orphans: 3; widows: 3; }
h1,h2,h3 { break-after: avoid; line-height: 1.2; font-weight: 700; }
h1 { margin: 0 0 17pt; font-size: 23pt; color: #102a3d; letter-spacing: -.5pt; }
h2 { margin: 17pt 0 7pt; font-size: 12.6pt; color: #075d68; }
h3 { margin: 13pt 0 6pt; font-size: 10.7pt; }
a { color: #006b79; text-decoration: none; overflow-wrap: anywhere; }
strong { color: #102a3d; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: .85em; overflow-wrap: anywhere; }
p code, td code, li code { background: #edf2f5; padding: 0 2pt; }
pre { background: #eef3f7; border-left: 2.8pt solid #0b7883; padding: 9pt 10pt; margin: 10pt 0 12pt; white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.43; break-inside: avoid; }
pre code { font-size: 7.45pt; padding: 0; background: transparent; }
blockquote { margin: 12pt 0; padding: 10pt 12pt; border-left: 3pt solid #00a394; background: #ecf7f5; }
blockquote p:last-child { margin-bottom: 0; }
ul,ol { padding-left: 17pt; margin: 7pt 0 11pt; }
li { padding-left: 2pt; margin-bottom: 5pt; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; break-inside: avoid; margin: 9pt 0 12pt; font-size: 8.4pt; line-height: 1.4; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: #17394a; color: white; padding: 8pt; text-align: left; font-weight: 700; vertical-align: top; }
th:first-child { width: 27%; }
td { border-bottom: .7pt solid #d6e0e6; padding: 8pt; vertical-align: top; overflow-wrap: anywhere; }
tr:nth-child(even) td { background: #f3f6f8; }
td p:last-child { margin-bottom: 0; }
hr { border: 0; border-top: 1pt solid #d1dfe6; margin: 17pt 0; }
.chapter, .toc, .overview-page { break-before: page; }
.chapter-label { font-size: 8pt; letter-spacing: 1.4pt; font-weight: bold; color: #087681; margin: 0 0 9pt; }
.cover { width: 210mm; height: 297mm; position: relative; background: #102a3d; color: #f4f8fb; padding: 27mm 22mm 20mm; overflow: hidden; }
.cover strong { color: inherit; }
.cover .brand { font-size: 15pt; letter-spacing: 4pt; font-weight: 700; color: #5de0c7; }
.cover .eyebrow { margin-top: 33mm; font-size: 9pt; letter-spacing: 1.8pt; text-transform: uppercase; color: #a9c1ce; }
.cover h1 { color: white; font-size: 37pt; line-height: 1.1; max-width: 158mm; margin: 13pt 0 15pt; }
.cover .subtitle { font-size: 15pt; color: #c1d8e0; max-width: 150mm; line-height: 1.4; }
.cover .rule { margin: 20pt 0; width: 35mm; border-top: 4pt solid #5de0c7; }
.cover .intro { font-size: 10.5pt; line-height: 1.65; max-width: 147mm; color: #dce8ed; }
.cover .pill { display: inline-block; border: .7pt solid #416777; padding: 6pt 8pt; margin: 0 4pt 6pt 0; font-size: 7.5pt; color: #d3ebe9; }
.cover .bottom { position: absolute; left: 22mm; right: 22mm; bottom: 20mm; padding-top: 13pt; border-top: .6pt solid #416777; font-size: 8pt; line-height: 1.7; color: #c2d6e0; }
.cover .bottom b { color: #5de0c7; }
.toc h1 { margin-bottom: 10pt; }
.toc .lead { font-size: 11pt; color: #536b7b; margin-bottom: 23pt; }
.toc-row { padding: 9pt 0; border-bottom: .6pt solid #dbe4e9; break-inside: avoid; font-size: 10pt; }
.toc-row a { color: #16394b; display: block; }
.toc-row a::after { content: target-counter(attr(href), page); float: right; color: #087681; font-weight: bold; }
.toc .note { font-size: 8.5pt; margin-top: 18pt; color: #526b7b; }
#chapter-08 { line-height: 1.43; }
#chapter-08 h2 { margin-top: 13pt; }
.references { font-size: 8.4pt; }
.references h2 { font-size: 10.3pt; margin: 10pt 0 4pt; }
.references p { margin-bottom: 3pt; }
.source-entry { break-inside: avoid; }
.overview-page { font-size: 10pt; line-height: 1.48; }
.overview-page h1 { font-size: 25pt; }
.overview-page h2 { margin-top: 17pt; }
.overview-page table { font-size: 8.6pt; }
'''


def render_md(text: str) -> str:
    body = MD.render(text)
    # Never produce local filesystem hyperlinks in a shared PDF.
    def safe_link(match: re.Match[str]) -> str:
        value = html.unescape(match.group(1))
        return match.group(0) if value.startswith(('https://','http://','#')) else ''
    return re.sub(r'href="([^"]*)"', safe_link, body)


def cover(title: str, subtitle: str, intro: str, pills: list[str], footer: str) -> str:
    return f'''<section class="cover">
      <div class="brand">TOMSEC</div>
      <div class="eyebrow">Cybersecurity homelab / classroom edition</div>
      <h1>{html.escape(title)}</h1>
      <div class="subtitle">{html.escape(subtitle)}</div>
      <div class="rule"></div>
      <p class="intro">{html.escape(intro)}</p>
      <div>{''.join('<span class="pill">'+html.escape(p)+'</span>' for p in pills)}</div>
      <div class="bottom"><b>EDITION 1.1 / 17 SEPTEMBER 2026</b><br>{html.escape(footer)}</div>
    </section>'''


def document(title: str, body: str) -> str:
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title><meta name="author" content="TomSec"><meta name="description" content="Sanitised classroom learning material with separate teaching examples and explicit validation boundaries."><style>{CSS}</style></head><body>{body}</body></html>'


def build() -> None:
    out = ROOT/'pdf'; out.mkdir(exist_ok=True)
    chapters = sorted((ROOT/'docs').glob('[0-9][0-9]-*.md'))
    bodies = []
    rows = []
    for i,p in enumerate(chapters):
        text=p.read_text(encoding='utf-8'); title=text.splitlines()[0].removeprefix('# ')
        anchor=f'chapter-{i:02d}'
        rows.append(f'<div class="toc-row"><a href="#{anchor}">{html.escape(title)}</a></div>')
        bodies.append(f'<section class="chapter" id="{anchor}"><p class="chapter-label">BUILD / EXPLAIN / VERIFY</p>{render_md(text)}</section>')
    for anchor, filename, label, cls in [('validation','VALIDATION.md','Validation record',''),('sources','SOURCES.md','Technical sources and provenance','references')]:
        rows.append(f'<div class="toc-row"><a href="#{anchor}">{label}</a></div>')
        appendix_html = render_md((ROOT/filename).read_text())
        if filename == 'SOURCES.md':
            pieces = re.split(r'(?=<h2>)', appendix_html)
            appendix_html = pieces[0] + ''.join('<div class="source-entry">'+piece+'</div>' for piece in pieces[1:])
        bodies.append(f'<section class="chapter {cls}" id="{anchor}">{appendix_html}</section>')
    front = cover('Cybersecurity\nhomelab projects','Self-hosting, hardening and custom proxying',
                  'Build private services, harden administration and separate private routing from internet egress. Reproduce the security method with new credentials, then verify access, failure behaviour and recovery.',
                  ['SELF-HOSTED SERVICES', 'SECURITY HARDENING', 'CUSTOM PROXY'],
                  'Reported original work is distinguished from new classroom configurations and unperformed deployment tests. No production credentials or private infrastructure export.')
    toc = '<section class="toc"><h1>Inside the handbook</h1><p class="lead">Start with scope. Build one service at a time. Verify before claiming success.</p>'+''.join(rows)+'<p class="note">Companion repository: class-project-pack. Use the Markdown and script files for copying long commands; PDF line wrapping is for reading. The separate overview is a short introduction for classmates.</p></section>'
    book_html=document('TomSec - Cybersecurity Homelab - Classroom Handbook',front+toc+''.join(bodies))
    HTML(string=book_html).write_pdf(out/'TomSec_Cybersecurity_Handbook.pdf')
    sections=(ROOT/'docs/PROJECT-OVERVIEW.md').read_text().split('<!-- PAGE -->')
    intro=cover('Cybersecurity\nprojects to rebuild','Homelab, security hardening and custom proxy',
                'A shareable introduction to the original project ideas and the separate classroom builds. Read this first, then use the detailed handbook and repository to try an exercise yourself.',
                ['PRIVATE SERVICES', 'HARDENING', 'PRIVACY ROUTING'],
                'Original builds are reported from project history, not freshly audited. Teaching examples are new adaptations, not copies of the live systems.')
    # The Markdown introduction remains editable in the repo; the cover contains its print summary.
    overview=intro+''.join('<section class="overview-page">'+render_md(s.strip())+'</section>' for s in sections[1:])
    HTML(string=document('TomSec - Cybersecurity Project Overview',overview)).write_pdf(out/'TomSec_Cybersecurity_Project_Overview.pdf')
    print('Built both PDFs under pdf/.')


if __name__=='__main__':
    build()
