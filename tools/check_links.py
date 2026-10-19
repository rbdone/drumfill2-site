#!/usr/bin/env python3
"""Checks every internal link and image on the site: files exist, #anchors exist, and every
feature-list link lands on a guide that shows at least one key picture. Exit 1 on any problem.
Usage: python3 tools/check_links.py"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs = set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.refs.append((tag, k, a[k]))
        if tag == "img" and "alt" not in a:
            self.refs.append((tag, "missing-alt", a.get("src", "?")))


pages = {}
for f in ROOT.rglob("*.html"):
    if "tools" in f.parts or ".git" in f.parts:
        continue
    p = Page()
    p.feed(f.read_text())
    pages[f.resolve()] = p

errors, external = [], set()
for f, p in pages.items():
    for tag, kind, ref in p.refs:
        rel = f.relative_to(ROOT)
        if kind == "missing-alt":
            errors.append(f"{rel}: <img src={ref}> has no alt")
            continue
        if ref.startswith(("http://", "https://")):
            external.add(ref)
            continue
        if ref.startswith(("mailto:", "data:")):
            continue
        path, frag = urldefrag(ref)
        target = f if not path else (f.parent / urlparse(path).path)
        if target.is_dir():
            target = target / "index.html"
        target = target.resolve()
        if not target.exists():
            errors.append(f"{rel}: {ref} -> missing file")
            continue
        if frag:
            tp = pages.get(target)
            if tp is None or frag not in tp.ids:
                errors.append(f"{rel}: {ref} -> missing #{frag}")

# every feature in the feature list -> guide section with a key picture
index = (ROOT / "index.html").read_text()
features = re.search(r'<section id="features".*?</section>', index, re.S).group(0)
links = re.findall(r'href="(guides/[^"]+)"', features)
for link in links:
    file, frag = link.split("#")
    text = (ROOT / file).read_text()
    m = re.search(rf'<section class="guide" id="{re.escape(frag)}".*?</section>', text, re.S)
    if not m:
        errors.append(f"feature {link}: no guide section")
    elif 'class="btnimg' not in m.group(0):
        errors.append(f"feature {link}: guide has no key picture")

print(f"{len(pages)} pages, {sum(len(p.refs) for p in pages.values())} links/images checked, "
      f"{len(links)} feature links → guides with key pictures")
print("external links (not fetched):")
for e in sorted(external):
    print("  ", e)
if errors:
    print(f"{len(errors)} PROBLEM(S):")
    for e in errors:
        print("  ", e)
    sys.exit(1)
print("OK: no broken internal links")
