"""A product team of Gemini 4 Argon agents reviews one build in parallel, then a CTO agent merges their findings.

Usage: python tools/team.py BUILD_HTML OUT_DIR [--tester-notes FILE]
Writes OUT_DIR/review_<role>.md for each role and OUT_DIR/cto_plan.md.
"""
import concurrent.futures as cf, pathlib, sys, time
from google import genai
from google.genai import types

ROLES = {
    "product_manager": "Product Manager for a game played by a 3-year-old with his parents. Judge fun, delight and replay value.",
    "child_ux": "Child-development and UX specialist for ages 2-4. Judge whether a child who cannot read understands what to do, "
                "motor-skill fit of the controls, frustration risks, and over-stimulation.",
    "art_director": "Art Director. The target look is bold, saturated, candy-bright stylized cartoon art in the spirit of today's "
                    "most colourful kids' and battle-royale-style games (original designs only). Judge colour, lighting, "
                    "toon shading, outlines, sky, and juice. The current build looks pale and washed out.",
    "game_designer": "Game Designer. Judge the core loop (find flame, splash, celebrate, next flame), pacing, rewards, the "
                     "kitten rescue, the cooperative two-controller play, and the team-splash moment.",
    "qa_tester": "QA Engineer. Find concrete bugs by reading the code: logic errors, edge cases, stuck states, input bugs "
                 "(multi-touch, pointer capture, release), camera problems, spawn problems, resize/orientation, audio unlock on iOS.",
    "performance": "Performance Engineer for an older iPad in Safari. Find costly patterns: draw calls, allocations per frame, "
                   "particle pools, geometry/material reuse, pixel ratio, overdraw.",
    "security_privacy": "Security and Privacy Architect for a children's product. Check: no network calls beyond the pinned three.js "
                        "CDN, no tracking, no personal data, safe localStorage use, no way to spend real money, no external links, "
                        "COPPA-friendly, no XSS-style innerHTML with dynamic data.",
    "accessibility": "Accessibility Lead. Judge touch-target sizes, contrast, sound levels and caps, speech cues, reduced-motion "
                     "fallback, and colour-blind-safe signalling.",
}
TEMPLATE = """You are the {role} on a small team shipping "Splash Town", a 3D fire-truck browser game for a 3-year-old on an
iPad (touch), with optional parent controllers. Review the game below from YOUR role only.

{notes}
Return at most 8 findings, most important first, as a numbered list. For each: a one-line problem, why it matters for a
3-year-old (or the parents), and the exact concrete change to make in the code (name the function or section). Be
specific and practical; no praise, no generic advice. Do not rewrite the whole file.

=== index.html ===
{html}
"""
CTO = """You are the CTO. Your team reviewed the game below. Merge their findings into ONE prioritized change list for a
single engineer who will rewrite the file in one pass tonight. Drop duplicates and anything risky or out of scope; keep the
game a single self-contained HTML file with three.js r128 from cdnjs. Order: (1) anything that breaks or blocks play,
(2) what a 3-year-old needs to understand and enjoy it, (3) the bright, saturated cartoon look, (4) co-op and rewards,
(5) performance, (6) privacy/safety. Max 25 items, each one line, concrete and testable.

{reviews}
"""


def ask(client, prompt):
    for attempt in range(3):
        try:
            r = client.models.generate_content(
                model="gemini-4-argon", contents=prompt,
                config=types.GenerateContentConfig(max_output_tokens=8000,
                                                   thinking_config=types.ThinkingConfig(thinking_level="medium")))
            return r.text or ""
        except Exception as e:
            time.sleep(3 * (attempt + 1)); err = e
    return f"(failed: {err!r})"


if __name__ == "__main__":
    html = pathlib.Path(sys.argv[1]).read_text()
    out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    notes = ""
    if "--tester-notes" in sys.argv:
        notes = "Notes from a human playtest:\n" + pathlib.Path(sys.argv[sys.argv.index("--tester-notes") + 1]).read_text()
    client = genai.Client()
    t0 = time.time()
    with cf.ThreadPoolExecutor(len(ROLES)) as pool:
        futs = {pool.submit(ask, client, TEMPLATE.format(role=desc, notes=notes, html=html)): name
                for name, desc in ROLES.items()}
        reviews = {}
        for f in cf.as_completed(futs):
            name = futs[f]; reviews[name] = f.result()
            (out / f"review_{name}.md").write_text(reviews[name])
            print(f"{time.time() - t0:6.1f}s  {name}: {len(reviews[name])} chars", flush=True)
    merged = "\n\n".join(f"### {n}\n{r}" for n, r in reviews.items())
    plan = ask(client, CTO.format(reviews=merged) + "\n=== index.html ===\n" + html)
    (out / "cto_plan.md").write_text(plan)
    print(f"{time.time() - t0:6.1f}s  cto_plan: {len(plan)} chars", flush=True)
