1. **Hidden Garage child elements swallow touches on the Water and Siren buttons (`pointer-events: auto` overrides hidden parent).**
   - **Why it matters for a 3-year-old:** When the child taps the big blue Water button or red Siren button, `.garage-side-col` and `.garage-bottom-bar` intercept the touch even though `#garageOverlay` is invisible (`opacity: 0`), completely breaking water spraying and causing immediate frustration.
   - **Exact change:** In `<style>`, add `visibility: hidden;` to `#garageOverlay` and `visibility: visible;` to `#garageOverlay.open`. Also change `.garage-side-col` and `.garage-bottom-bar` from `pointer-events: auto;` to `pointer-events: none;`, and add `#garageOverlay.open .garage-side-col, #garageOverlay.open .garage-bottom-bar { pointer-events: auto; }`.

2. **Tapping a flame or house on screen does not turn the truck if the tap lands near the screen center (12px deadzone around a fixed screen-center anchor).**
   - **Why it matters for a 3-year-old:** A 3-year-old's natural motor instinct is to tap or press directly on the thing they want to go to (or tap just above the truck). Because `steerAnchorX/Y` is hardcoded to `(innerWidth * 0.5, innerHeight * 0.55)` with a `Math.hypot(dx, dy) > 12` deadzone, pressing near the middle of the screen drives the truck in whatever old direction it was facing instead of toward the finger.
   - **Exact change:** In `animate()` under `// --- CHILD FIRE TRUCK MOVEMENT & STEERING ---`, project `fireTruck.group.position` to screen space each frame to serve as the steering origin, and lower the deadzone:
     ```js
     const truckScreen = fireTruck.group.position.clone().project(camera);
     const originX = (truckScreen.x * 0.5 + 0.5) * window.innerWidth;
     const originY = (-truckScreen.y * 0.5 + 0.5) * window.innerHeight;
     const dx = steerCurX - originX;
     const dy = steerCurY - originY;
     if (Math.hypot(dx, dy) > 4) {
     ```

3. **Truck gets pinned and half-hidden behind perimeter hills near the fence (`hillPositions` have no collision and `WORLD_RADIUS` only adds `0.6` rad to angle).**
   - **Why it matters for a 3-year-old:** Driving into a hill/fence corner traps the truck inside the hill geometry where the child cannot see it or steer out easily, causing confusion and helplessness.
   - **Exact change:**
     - In Section 4 (`Soft Rolling Green Hills`), register each hill in `obstacles` so the truck smoothly slides around them: inside `hillPositions.forEach(hp => { ... })`, add `obstacles.push({ x: hp.x, z: hp.z, r: hp.r * 0.85, mesh: hm });` and reduce `WORLD_RADIUS` from `54` to `48`.
     - In `animate()` under `// Soft world bounds & friendly obstacle bounces`, replace `fireTruck.angle += 0.6;` with a gentle inward push and steer-toward-center:
       ```js
       const toCenterAngle = Math.atan2(fireTruck.x, fireTruck.z);
       fireTruck.angle = toCenterAngle;
       fireTruck.x = nx * (WORLD_RADIUS - 1.5);
       fireTruck.z = nz * (WORLD_RADIUS - 1.5);
       ```

4. **Trees, houses, and flames directly south (`+Z`) of the truck block the camera's view of the truck and kitten rescate.**
   - **Why it matters for a 3-year-old:** At age 3, losing sight of their character ("where did my truck go?") breaks object permanence confidence and makes it hard to tell if water is hitting the flame.
   - **Exact change:** In `animate()` under `// --- SMOOTH CAMERA FRAMING ---` (when `!isGarageOpen`), raise the camera angle slightly (`desiredCamPos` Y from `17.5` to `22.0`, Z from `22.5` to `20.0`) and fade any obstacle or flame sitting between the camera and the truck:
     ```js
     obstacles.forEach(ob => {
       const inFront = ob.z > fireTruck.z + 0.5 && ob.z < camera.position.z && Math.abs(ob.x - fireTruck.x) < 4.5;
       ob.mesh.traverse(c => {
         if (c.isMesh && c.material) {
           c.material.transparent = inFront;
           c.material.opacity = inFront ? 0.35 : 1.0;
         }
       });
     });
     ```

5. **Tapping the Water button briefly instead of holding it stops spraying before the flame can be extinguished.**
   - **Why it matters for a 3-year-old:** 2-to-4-year-olds frequently poke/tap buttons repeatedly rather than maintaining a sustained press-and-hold. Currently `endSteerPointer` sets `fireTruck.spraying = false` the millisecond their finger lifts, so single taps barely tickle the flame.
   - **Exact change:** Add `let sprayHoldTimer = 0;` near `fireTruck`. In `btnWaterEl` `pointerdown`, set `sprayHoldTimer = 0.65;`. In `animate()`, decrement `sprayHoldTimer = Math.max(0, sprayHoldTimer - dt);` and keep `fireTruck.spraying = waterButtonPointers.size > 0 || sprayHoldTimer > 0;` so every tap produces a full, satisfying burst of water.

6. **Washed-out pastel 3D appearance reduces visual figure-ground separation for young eyes.**
   - **Why it matters for a 3-year-old:** Young children rely on high-contrast, high-chroma primary/candy colors and strong dark outlines to quickly parse 3D objects from the background. Overly bright hemisphere lighting, warm fog, and a high-floor toon ramp wash out the red truck, yellow stars, and green grass.
   - **Exact change:** In Section 3 (`THREE.JS SCENE, CAMERA, TOON SHADING`):
     - Remove or reduce fog: change `scene.fog = new THREE.FogExp2(0xffd8b8, 0.0042);` to `scene.fog = new THREE.FogExp2(0x54d2ff, 0.0015);`.
     - Lower `hemiLight` intensity from `0.78` to `0.45` and increase `dirLight` intensity from `0.72` to `0.95`.
     - Darken the shadow step in `toonGradData` from `[145, 145, 145, 255, 210, 210, 210, 255, 255, 255, 255, 255]` to `[85, 85, 95, 255, 185, 185, 195, 255, 255, 255, 255, 255]`.
     - Change `outlineMat` color from `0x1e272e` to pure black `0x0a0e14` and default `addOutline` scale from `1.07` to `1.09`.
     - Deepen the road color `roadMat` from `0xf5e6c8` to `0xffb142` or `0xd1ccc0` so the yellow guide trail (`0xfff200`) pops with high contrast against the road.

7. **Locked Garage items trigger a spoken "Splash more fires for stars!" prompt that non-verbal/pre-counting 3-year-olds cannot connect to the Star Jar.**
   - **Why it matters for a 3-year-old:** When a 3-year-old taps a locked hat or paint color and hears a reject boing, they don't know *why* it didn't unlock because their attention is on the button they tapped, not the Star Jar in the top-left corner.
   - **Exact change:** In `renderGarageItems()` inside the `else` branch (not enough stars), pulse the `#starJar` simultaneously with the button wiggle so the child's eye is drawn to the Star Jar:
     ```js
     starJarEl.classList.remove('bounce');
     void starJarEl.offsetWidth;
     starJarEl.classList.add('bounce');
     setTimeout(() => starJarEl.classList.remove('bounce'), 450);
     ```

8. **Top-left `#btnGarage` stays clickable and visible while the Garage overlay is already open.**
   - **Why it matters for a 3-year-old:** `#topLeftCluster` has `z-index: 28` (above `#garageOverlay` at `z-index: 25`), so both the top-left Garage icon and the top-right green Play/Go button (`#btnCloseGarage`) are on screen at once, competing for attention.
   - **Exact change:** In `btnGarageEl` `pointerdown` and `#btnCloseGarage` `pointerdown`, toggle `btnGarageEl.style.display = isGarageOpen ? 'none' : 'flex';` so only the Star Jar remains in the top-left corner while inside the Garage, leaving the big pulsing green Play button (`#btnCloseGarage`) as the single unmistakable exit action.