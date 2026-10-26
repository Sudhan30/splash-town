You are writing a complete, polished 3D browser game for a 3-YEAR-OLD child who loves fire trucks and cars,
to be played on an iPad (Safari, landscape, touchscreen), together with their parents. Write it as ONE file.

GAME: "Splash Town"
A small, soft, round, toy-like town (low-poly, bright, cheerful, high contrast: green grass hills, a few round
houses with colourful roofs, round trees, a pond, a little bridge, winding road loops, fences as soft borders).
Silly cartoon flames with friendly faces (two eyes, smile) pop up on houses, trees and hills. Spraying water on a
flame makes it giggle, then turn into a burst of flowers and a small rainbow arc, with confetti and a happy chime.
A new flame lights up somewhere else within a few seconds. It never ends; there is NO way to lose.

PLAYERS (all on one iPad screen, cooperative, never competitive):
1. CHILD: a chunky red fire truck (cab, ladder, flashing light bar, big wheels), controlled by TOUCH:
   - Touch and drag anywhere on the screen (except the two buttons) to steer: the truck turns toward the drag
     direction relative to the screen center (or relative to where the finger first touched), and drives forward
     automatically while a finger is down; when released it rolls to a gentle stop. No reverse, no gears.
   - WATER button: a huge round button bottom-right (about 25% of screen height), drawn as a big blue water drop
     (CSS/SVG, no text). Holding it sprays a stream of water particles that AUTO-AIMS at the nearest flame within
     a forward cone and range; if no flame is near, it sprays forward anyway (always fun).
   - SIREN button: a huge round button bottom-left, a red flashing light (no text). Tap: siren sound (two-tone,
     2 seconds), the light bar flashes red/blue, the truck does a little happy bounce.
   - Mouse also works (for testing on a laptop): click-drag steers, the buttons are clickable.
2. PARENT 1: a blue water-tanker truck, appears only when a first game controller connects (Gamepad API,
   standard mapping; must work with Nintendo Switch Pro Controller / Joy-Con, Xbox, PlayStation pads paired to the
   iPad): left stick steers (arcade style, forward on stick up), button 0 (A/bottom face) sprays water, button 1
   honks a cheerful horn. Driving close to the fire truck plays a "glug" refill moment (water bubbles float from
   tanker to fire truck, both trucks do a little hop) - purely for fun; the child's water never runs out.
3. PARENT 2: a yellow helicopter (body, spinning rotor, skids), appears when a SECOND controller connects. It flies
   at a fixed low height over the town: left stick moves it, button 0 drops a big water splash straight down onto
   whatever is below (great for flames on roofs and hills), button 1 does a happy loop/wiggle with a whirr sound.
   Its shadow on the ground shows where the water will land.
   A controller that sends no input for 60 seconds lets its vehicle park and go to sleep (zZz), still visible, so the
   game always works solo for the child. Vehicles reconnect instantly on input.

TEAMWORK MOMENT: if two or three vehicles splash the SAME flame within 2 seconds, it becomes a TEAM SPLASH: a giant
rainbow, fireworks, everyone's vehicle does a jump, and a big cheer sound. A few flames are extra-big "family
flames" that wobble and need a little longer to put out, so teaming up feels natural (the child alone can still
put them out, just slower).

KITTEN: a kitten sits in one tree with a little flame next to it. When that flame is splashed, the kitten hops
onto the fire truck's ladder and rides along (bobbing), meowing happily now and then. Later another kitten appears
in another tree, and so on, up to 3 kittens riding on top. Each rescue gets a special celebration.

MUST BE EASY TO UNDERSTAND FOR A 3-YEAR-OLD WHO CANNOT READ:
- No text anywhere on screen. No menus, no score, no timer, no pause screen, no "game over", no settings screens.
- Start: the scene is already running. A big friendly cartoon hand (drawn with CSS/SVG) appears over the screen and
  SHOWS the drag-to-drive motion (animated swipe), then shows pressing the water button, looping until the child
  touches the screen. It reappears after 10 seconds without any touch.
- A soft glowing dotted trail on the ground always leads from the fire truck to the nearest flame. The target flame
  bounces and waves. When the fire truck is close enough to spray it, the water button pulses and glows.
- A friendly spoken voice using the Web Speech API (speechSynthesis, en-US, rate ~0.95, pitch ~1.2): short cues like
  "Find the fire!", "Splash!", "Yay! Flowers!", "Team splash!", "You saved the kitty!", "Nee-naw!". At most one cue
  every 4 seconds, never overlapping. Must not break if speechSynthesis is missing.
- Every touch gives instant feedback: a sparkle at the touch point and a soft "pop" sound.
- The camera: a smooth, slightly tilted third-person view behind/above the fire truck; when other vehicles are
  active, it smoothly frames ALL active vehicles (zooming out a little when they spread apart, with a sensible max
  zoom). Never jerky.
- Soft world bounds: fences and gentle invisible walls keep everyone in town; bumping into houses, trees or each
  other is a friendly bounce with a "boing" sound, never a crash.

ART STYLE (important): a vivid, stylized cartoon look in the spirit of today's most colourful kids' and
battle-royale-style games (think bold, saturated, candy-bright colours; chunky rounded shapes with exaggerated
proportions; toon/cel shading). Do NOT copy any existing game's characters, logos or assets: all designs original.
- Palette: saturated hues (cherry red fire truck, electric blue tanker, sunny yellow helicopter, lime-green grass,
  hot-pink and purple flowers, turquoise pond, orange-magenta flames), never muddy or grey.
- Toon shading: use THREE.MeshToonMaterial with a 3-step gradientMap built from a tiny DataTexture, plus a soft
  hemisphere light and one warm directional light. Add bold dark outlines to vehicles and characters with the
  inverted-hull trick (a slightly scaled BackSide black mesh), cheaply.
- A gradient sky (big inverted sphere with a vertex-coloured or shader gradient: deep blue at top to warm
  peach at the horizon), fluffy chunky clouds drifting, gentle colour-graded fog.
- Juicy effects everywhere: squash-and-stretch on jumps and splashes, bouncy idle animations on houses, trees and
  flowers, sparkly glowing particles (additive blending) for water, confetti and rainbows, a bright rim/glow on the
  target flame.

AUDIO: everything synthesized with the Web Audio API (no audio files): soft engine hum that rises with speed, siren,
water spray noise, splash, giggle, chime, horn, helicopter whirr, meow, cheer, pop, boing, glug. Master volume
modest and capped. iOS requires a user gesture before audio: create/resume the AudioContext on the first touch.
A small parent-only mute control in the top-right corner: invisible until long-pressed for 2 seconds (toggles all
sound and speech; shows a tiny speaker icon briefly). Nothing else in the corners.

TECH RULES (follow exactly):
- One self-contained HTML file. Load three.js only from https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
  (global THREE). No other external resources: no images, fonts, audio files or other scripts. All models are built
  from three.js primitives in code; all icons are inline SVG or CSS.
- Mobile web-app meta tags: viewport (width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no,
  viewport-fit=cover), apple-mobile-web-app-capable, apple-mobile-web-app-status-bar-style, theme-color, a title
  "Splash Town". CSS: html/body fill the screen, no scroll, no text selection, no callouts, touch-action: none,
  respect safe-area insets for the buttons.
- Prevent all browser gestures from interfering (pinch zoom, double-tap zoom, pull-to-refresh, long-press menu):
  preventDefault on touch events where needed, passive:false listeners.
- Use pointer events with multi-touch support (a drag finger and a button finger at the same time).
- Performance for older iPads: renderer.setPixelRatio(Math.min(devicePixelRatio, 2)), antialias on, simple
  MeshLambert/MeshToon-like materials, at most one directional light plus ambient/hemisphere light, cheap fake blob
  shadows (dark circles) instead of shadow maps, instanced or pooled particles (water, confetti, sparkles), keep
  draw calls modest. Handle resize and orientation changes. Use requestAnimationFrame with delta time clamped.
- Robust: no alert/confirm/prompt; wrap speech and gamepad code so missing APIs never throw; no console errors.
- When the tab is hidden, pause audio; resume on return.

OUTPUT FORMAT (follow exactly): output exactly this and nothing else:
<<<FILE path=index.html>>>
...the complete HTML file...
<<<END FILE>>>
No markdown fences, no commentary before or after. The file must be complete and runnable; do not leave
placeholders, TODOs or "rest omitted". Make it genuinely delightful: smooth animation, bouncy squash-and-stretch,
bright colours, little surprises (a duck in the pond that quacks when you drive by, flowers that sway, clouds).
