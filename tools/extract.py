"""Pull index.html out of an Argon run's stream.txt and do quick static checks."""
import pathlib, re, sys
name = sys.argv[1]
txt = pathlib.Path(f"runs/{name}/stream.txt").read_text(errors="replace")
m = re.search(r"<<<FILE path=index\.html>>>\n?(.*?)<<<END FILE>>>", txt, re.S)
if not m:
    print(f"{name}: no complete file block"); sys.exit(1)
html = re.sub(r"^```\w*\n|```\s*$", "", m.group(1).strip())
out = pathlib.Path(f"builds/{name}"); out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(html)
checks = {"three r128": "three.js/r128/three.min.js" in html, "touch/pointer": "pointerdown" in html,
          "gamepad": "getGamepads" in html, "audio": "AudioContext" in html, "speech": "speechSynthesis" in html,
          "toon": "MeshToonMaterial" in html, "garage": "localStorage" in html, "closes </html>": "</html>" in html.lower(),
          "no alert": "alert(" not in html}
print(f"{name}: {len(html):,} chars | " + " ".join(f"{k}:{'ok' if v else 'MISSING'}" for k, v in checks.items()))
