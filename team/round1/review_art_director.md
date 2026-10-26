1. **Over-bright lighting and a washed-out toon ramp flatten all 3D forms into pale pastels.**
   - **Why it matters:** A 3-year-old relies on bold, high-contrast toy-like value separation to instantly read 3D shapes against the background.
   - **Exact change:** In Section 3 (`THREE.JS SCENE, CAMERA, TOON SHADING & WORLD SETUP`), lower `hemiLight` intensity and give it a deep royal-blue ground bounce: `const hemiLight = new THREE.HemisphereLight(0xffffff, 0x1e3799, 0.35);`. Change `dirLight` to pure crisp white and higher contrast: `const dirLight = new THREE.DirectionalLight(0xffffff, 1.15);`. Deepen the shadow and midtone steps in `toonGradData` to `new Uint8Array([70, 70, 95, 255, 165, 165, 185, 255, 255, 255, 255, 255])`.

2. **Milky peach distance fog (`0xffd8b8`) desaturates the entire town, sky, and horizon.**
   - **Why it matters:** Pale haze kills the candy-bright cartoon vibrancy and makes distant flames and landmarks look muddy and hard to spot.
   - **Exact change:** In Section 3, change `scene.fog` to a vibrant cyan-blue with much lower density: `scene.fog = new THREE.FogExp2(0x00c3ff, 0.0015);`. In the `Gradient Sky Sphere` block, replace `topCol`, `midCol`, and `botCol` with saturated candy blues and warm gold: `topCol = new THREE.Color(0x0044ff)`, `midCol = new THREE.Color(0x00c8ff)`, `botCol = new THREE.Color(0xffe600)`.

3. **Terrain, road, and house wall colours use low-chroma cream and chalky green hex values.**
   - **Why it matters:** Washed-out ground and off-white walls blend together under bright light instead of popping like chunky plastic toys.
   - **Exact change:** In Section 4 (`TOWN ENVIRONMENT...`), change `grassMat` to `makeToonMat(0x20bf3b)`, `oceanMat` to `makeToonMat(0x0066ff)`, `beachMat` to `makeToonMat(0xffc82c)`, `roadMat` to `makeToonMat(0xffaa55)`, and `leafMat2` to `makeToonMat(0x10ac84)`. In `houseConfigs`, replace the pale cream/white `wall` colours (`0xfff6e5`, `0xeaf6ff`, etc.) with saturated candy hues (`0xffdd33`, `0x48dbfb`, `0xff9ff3`, `0x54a0ff`, `0xff9f43`, `0x1dd1a1`).

4. **The hidden `#garageOverlay` children (`pointer-events: auto`) block the Water button and prevent any water splash juice from ever triggering.**
   - **Why it matters:** If the child taps the big blue Water button and nothing happens because an invisible UI bar eats the touch, the core visual payoff (water stream, rainbows, confetti) is completely broken.
   - **Exact change:** In the `<style>` block for `.garage-side-col` and `.garage-bottom-bar`, remove `pointer-events: auto;` and add `#garageOverlay.open .garage-side-col, #garageOverlay.open .garage-bottom-bar { pointer-events: auto; }`, or set `visibility: hidden;` on `#garageOverlay` and `visibility: visible;` on `#garageOverlay.open`.

5. **Foreground trees, houses, and flames between the camera and the fire truck completely hide the truck from view.**
   - **Why it matters:** When a tree or big flame blocks the truck, a 3-year-old loses visual contact with their toy truck and gets confused about where they are spraying.
   - **Exact change:** In Section 13 (`animate`), inside the `SMOOTH CAMERA FRAMING` block, raise the camera pitch (`desiredCamPos.y = 22.0 + zoomExtra * 0.75`) and check each obstacle in `obstacles` and flame in `activeFlames`: if its Z is between `fireTruck.z + 1` and `camera.position.z - 2` and `Math.abs(ob.x - fireTruck.x) < 4.5`, smoothly scale it down (`ob.mesh.scale.setScalar(0.25)`) or set material opacity to `0.3` so the truck silhouette stays 100% clear.

6. **Inverted-hull outlines (`scale = 1.05`–`1.07`) are too thin and grey-tinted (`0x1e272e`), and key props lack outlines entirely.**
   - **Why it matters:** Crisp, ink-black cartoon outlines are essential to give low-poly shapes a punchy, battle-royale/kids-cartoon illustration look.
   - **Exact change:** In Section 3 (`addOutline`), change `outlineMat` color to pure ink black (`0x0a0a12`) and increase the default `scale` parameter from `1.07` to `1.10`. In Section 4, call `addOutline(hm, 1.04)` on each hill mesh in `hillPositions.forEach(...)` and `addOutline(pm, 1.06)` on each cloud puff in `clouds`.

7. **Driving into the perimeter fence and outer hills traps the truck at the world edge and lets the camera clip into hills.**
   - **Why it matters:** Getting visually wedged behind a hill breaks the toy-world illusion and hides the truck behind geometry.
   - **Exact change:** In Section 4, add `hillPositions` to the `obstacles` array (`obstacles.push({ x: hp.x, z: hp.z, r: hp.r * 0.85, mesh: hm })`). In Section 13 (`Soft world bounds`), reduce the driving boundary to `WORLD_RADIUS - 3.5` and, on contact, push `fireTruck.x` and `fireTruck.z` inward by `2.5` units toward `(0,0)` while steering `fireTruck.angle` toward `Math.atan2(fireTruck.x, fireTruck.z)` so it bounces cleanly back into town.

8. **Water spray particles use `THREE.AdditiveBlending` with pale white (`0xffffff`), washing out to invisible white over bright grass and houses.**
   - **Why it matters:** The water stream is the hero visual effect; if it blends into white over bright surfaces, spraying feels weak and unsatisfying.
   - **Exact change:** In Section 8 (`POOLED PARTICLES`), change `partGeo` material from `blending: THREE.AdditiveBlending` to `blending: THREE.NormalBlending`, increase `partGeo` radius to `0.36`, and in `handleWaterSpray` (Section 12), emit alternating vivid cyan (`0x00a8ff`) and deep electric blue (`0x0055ff`) droplets with a dark outline or higher opacity (`1.0`).