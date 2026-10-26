# Splash Town

A 3D fire-truck game for a 3-year-old, made as a family Thanksgiving gift. Drive the little red fire truck, splash
silly flames into flowers and rainbows, rescue kittens, and earn stars for the Garage (paint, hats, stickers, horn
sounds). Parents can join with game controllers: a blue water tanker and a yellow helicopter, all cooperative.

- **Plays in the browser** on iPad, iPhone, Android phones and tablets, and laptops. Touch for the child; Nintendo
  Switch Pro Controller / Joy-Con, Xbox or PlayStation pads for parents.
- **No reading needed, no way to lose, no real-money purchases, no tracking.**
- **Written by Gemini 4 Argon.** `prompts/` holds the spec; `builds/` holds each generation; `team/` holds an
  8-role review (product, child UX, art, game design, QA, performance, security and privacy, accessibility) and the
  merged CTO plan that drove each rewrite.

To play locally: `python3 -m http.server -d builds 8010`, then open `http://localhost:8010/<build>/index.html`.
