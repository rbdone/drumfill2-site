# DrumFill2 website

The public site for DrumFill2, an Android drum app for practice and live play:
<https://rbdone.github.io/drumfill2-site/>

Plain static HTML, CSS and JavaScript served by GitHub Pages (no build step; `.nojekyll`).
The APK and `SHA256SUMS.txt` are attached to this repository's GitHub releases.

- `index.html`: home page (hero with a playable toy drum machine, problems, workflows, features, praise, download, FAQ)
- `guides/`: step-by-step how-to pages with pictures of the keys to tap
- `img/screens/`, `img/buttons/`: screenshots of the app and crops of its keys (WebP)
- `tools/build_guides.py`: regenerates `guides/*.html` from the content in the script (output is committed)
- `tools/check_links.py`: checks every internal link, anchor and image alt text

Preview locally: `python3 -m http.server` in this folder, then open <http://localhost:8000/>.

The "Praise" quotes are invented parody. DrumFill2 is not affiliated with any drum machine maker.
