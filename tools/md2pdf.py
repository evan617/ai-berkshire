#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown 轉高質量 PDF（中文友好，Chrome headless 渲染）
用法: python3 md2pdf.py <input.md> <output.pdf>
"""
import sys
import subprocess
from pathlib import Path

import markdown


CSS = """
@page {
  size: A4;
  margin: 16mm 14mm 16mm 14mm;
}
* { box-sizing: border-box; }
body {
  font-family: "PingFang SC", "Helvetica Neue", -apple-system, "Apple Color Emoji", "Segoe UI Emoji", sans-serif;
  font-size: 10.5pt;
  line-height: 1.68;
  color: #1f2328;
  margin: 0;
}
h1 {
  font-size: 21pt;
  border-bottom: 2.5px solid #24292f;
  padding-bottom: 8px;
  margin-top: 0;
  margin-bottom: 14px;
  line-height: 1.3;
}
/* 第一个 h1 作为封面标题 */
body > h1:first-child {
  font-size: 26pt;
  text-align: center;
  border-bottom: none;
  padding-top: 40px;
  padding-bottom: 20px;
  color: #0d2b4e;
}
h2 {
  font-size: 15pt;
  color: #0d2b4e;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 5px;
  margin-top: 24px;
  page-break-after: avoid;
}
h3 {
  font-size: 12.5pt;
  color: #1f3a5f;
  margin-top: 18px;
  page-break-after: avoid;
}
h4 { font-size: 11pt; color: #333; margin-top: 14px; page-break-after: avoid; }
p { margin: 7px 0; }
strong { color: #0d2b4e; }
a { color: #0969da; text-decoration: none; }
ul, ol { margin: 7px 0; padding-left: 24px; }
li { margin: 3px 0; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 11px 0;
  font-size: 9.3pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #d0d7de;
  padding: 5px 8px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #eef2f7;
  font-weight: 600;
  color: #1f3a5f;
}
tbody tr:nth-child(even) { background: #fafbfc; }
blockquote {
  border-left: 3px solid #4a90d9;
  background: #f4f8fc;
  margin: 11px 0;
  padding: 9px 15px;
  color: #444;
  border-radius: 0 4px 4px 0;
  page-break-inside: avoid;
}
blockquote p { margin: 4px 0; }
code {
  font-family: "SF Mono", "Menlo", "Consolas", monospace;
  background: #eff1f3;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 9pt;
  color: #b02a37;
}
pre {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 5px;
  padding: 11px 13px;
  overflow-x: auto;
  page-break-inside: avoid;
  font-size: 8.8pt;
  line-height: 1.5;
}
pre code { background: none; padding: 0; color: #1f2328; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 20px 0; }
em { color: #555; }
/* 标题不与后续内容分离 */
h1, h2, h3, h4 { page-break-after: avoid; }
/* 大区块避免断裂 */
table, blockquote, pre { page-break-inside: avoid; }
"""


def md_to_html(md_path: str, html_path: str) -> None:
    text = Path(md_path).read_text(encoding='utf-8')
    body = markdown.markdown(
        text,
        extensions=['tables', 'fenced_code', 'sane_lists', 'attr_list'],
        output_format='html5',
    )
    html = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<style>' + CSS + '</style>\n'
        '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
    )
    Path(html_path).write_text(html, encoding='utf-8')


def html_to_pdf(html_path: str, pdf_path: str) -> None:
    chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    # file:// 需要绝对路径
    abs_html = Path(html_path).resolve().as_uri()
    cmd = [
        chrome,
        '--headless=new',
        '--disable-gpu',
        '--no-pdf-header-footer',
        '--run-all-compositor-stages-before-draw',
        '--virtual-time-budget=8000',
        f'--print-to-pdf={pdf_path}',
        abs_html,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> None:
    if len(sys.argv) != 3:
        print('用法: python3 md2pdf.py <input.md> <output.pdf>', file=sys.stderr)
        sys.exit(1)
    md_path, pdf_path = sys.argv[1], sys.argv[2]
    html_path = str(Path(pdf_path).with_suffix('.html'))
    md_to_html(md_path, html_path)
    html_to_pdf(html_path, pdf_path)
    size_kb = Path(pdf_path).stat().st_size / 1024
    print(f'✅ PDF 生成成功: {pdf_path} ({size_kb:.0f} KB)')


if __name__ == '__main__':
    main()
