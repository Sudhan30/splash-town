1. **Hidden Garage children steal touch input over the Water button (Playtest Blocker #1).**
   - **Why it matters:** A 3-year-old tapping or holding the bottom-right Water button has their touches swallowed by `.garage-bottom-bar` and `.garage-side-col` even when the Garage is closed, completely breaking water spraying.
   - **Concrete change:** In the `<style>` section, change `.garage-side-col` and `.garage-bottom-bar` from `pointer-events: auto;` to `pointer-events: none;`, add `visibility: hidden;` to `#garageOverlay`, and add rules: `#garageOverlay.open { visibility: visible; pointer-events: auto; }` and `#garageOverlay.open .garage-side-col, #garageOverlay.open .garage-bottom-bar { pointer-events: auto; }`.

2. **Washed-out 3D contrast and low-saturation toon shading (Playtest #2).**
   - **Why it matters:** Young children and users with low vision or colour-vision deficiency need high-chroma, high-contrast figures against the ground to visually separate the truck, guide trail, and targets.
   - **Concrete change:** In section `3. THREE.JS SCENE, CAMERA, TOON SHADING & WORLD SETUP`, darken the shadow and midtone steps of `toonGradData` to `new Uint8Array([85, 85, 85, 255, 175, 175, 175, 255, 255, 255, 255, 255])`, lower `hemiLight` intensity from `0.78` to `0.5`, increase `dirLight` intensity from `0.72` to `1.0`, reduce `scene.fog` density from `0.0042` to `0.0015`, and in `addOutline()` increase the default outline `scale` from `1.07` to `1.10` with `outlineMat` colour set to `0x0a0e14`.

3. **No `prefers-reduced-motion` fallback for continuous bouncing, flashing, and camera-zoom animations.**
   - **Why it matters:** Vestibular-sensitive children or parents can experience discomfort from the constant prop bouncing (`bouncyProps`), rapid 10Hz siren light-bar strobing, and pulsing UI buttons.
   - **Concrete change:** In `<style>`, add `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; } }`. In JavaScript section 13 (`animate`), define `const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;` and when true: set `speedBounce = 0`, `fireTruck.hopY = 0`, skip the `bouncyProps.forEach` scale loop, and replace the 10Hz `Math.floor(now * 10) % 2` siren strobe with a steady glow (`fireTruck.lightL.material.emissive.setHex(0xff1f3d)`).

4. **Uncapped audio peaks when multiple sounds overlap.**
   - **Why it matters:** Rapidly tapping Siren/Horn while spraying water and triggering chimes stacks multiple Web Audio oscillators without compression, creating sudden loud spikes that can startle a toddler or overwhelm a parent.
   - **Concrete change:** In `initAudio()` (section 2), insert a `DynamicsCompressorNode` between `masterGain` and `audioCtx.destination`:
     ```js
     const compressor = audioCtx.createDynamicsCompressor();
     compressor.threshold.setValueAtTime(-18, audioCtx.currentTime);
     compressor.knee.setValueAtTime(12, audioCtx.currentTime);
     compressor.ratio.setValueAtTime(12, audioCtx.currentTime);
     masterGain.disconnect();
     masterGain.connect(compressor);
     compressor.connect(audioCtx.destination);
     ```

5. **Parent Mute control is completely invisible (`opacity: 0`) and ignores `speechSynthesis` during active speech.**
   - **Why it matters:** Parents cannot discover an invisible (`opacity: 0`) top-right corner zone during a noisy moment, and muting does not immediately silence an in-progress spoken utterance or provide an accessible label.
   - **Concrete change:** In `#muteZone` CSS, change `opacity: 0;` to `opacity: 0.38; background: rgba(0,0,0,0.28); border: 2px solid rgba(255,255,255,0.6);` and add `role="button" aria-label="Hold 2 seconds to mute sound"` to `<div id="muteZone">`. In the `muteZone` `pointerdown` timeout callback (section 2), add `if (isMuted && 'speechSynthesis' in window) window.speechSynthesis.cancel();`.

6. **Garage item buttons (`.g-item`) are too small and tightly packed for 3-year-old fine motor skills.**
   - **Why it matters:** At `64px` with `8px` gap (`gap: 8px`), toddlers with developing motor precision will frequently mis-tap adjacent items or fail to hit the target cleanly on an iPad screen.
   - **Concrete change:** In `<style>`, increase `.g-item` base size from `width: 64px; height: 64px;` to `width: 78px; height: 78px;` (and `@media (min-width: 900px)` to `88px`), and increase `.garage-row-group` and `.garage-pill` `gap` from `8px` to `14px`.

7. **Yellow guide trail dots and target ring have poor contrast and colour-blind visibility against pale roads and sandy beaches.**
   - **Why it matters:** `0xfff200` (yellow) on `0xf5e6c8` (road) and `0xffe28a` (beach) has a luminance contrast ratio under 1.3:1, making the navigation aid invisible to colour-blind and low-vision players.
   - **Concrete change:** In section 7 (`trailDots` creation and `spawnFlame`), give each trail dot and `glowRing` a high-contrast dark outer ring by adding a child `THREE.RingGeometry(0.42, 0.58, 16)` mesh with `MeshBasicMaterial({ color: 0x1e272e })` underneath each `trailDots` mesh, and change `glowRing` in `spawnFlame()` to alternate or outline with `0x1e272e` so shape and luminance contrast carry the signal rather than hue alone.

8. **No spoken or audio guidance when theWater button becomes ready in range of a flame.**
   - **Why it matters:** A 3-year-old focused on dragging the truck may not notice the peripheral `#btnWater.pulse-glow` visual animation when arriving at a fire, missing the cue to press the water button.
   - **Concrete change:** In `animate()` (section 13, inside `if (targetFlame && !isGarageOpen)`), track range entry with a boolean `wasInSprayRange` and trigger a gentle spoken prompt when entering range:
     ```js
     const inRange = targetDist < 16.5;
     if (inRange && !fireTruck.wasInSprayRange && !fireTruck.spraying) {
       speakCue('Press water to splash!');
     }
     fireTruck.wasInSprayRange = inRange;
     ```