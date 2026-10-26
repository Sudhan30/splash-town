1. **Hidden Garage children steal touches from the Water and Siren buttons (`pointer-events: auto` overrides parent `none`).**
   - **Why it matters:** A 3-year-old cannot spray water or press the siren when the Garage is closed because `.garage-side-col` and `.garage-bottom-bar` have `pointer-events: auto` and higher z-index (`25` vs `10`), swallowing touches even at `opacity: 0`.
   - **Concrete fix:** In the `<style>` section, add `visibility: hidden;` to `#garageOverlay` and `visibility: visible;` to `#garageOverlay.open`, and remove `pointer-events: auto;` from `.garage-side-col` and `.garage-bottom-bar` (or scope them to `#garageOverlay.open .garage-side-col, #garageOverlay.open .garage-bottom-bar { pointer-events: auto; }`).

2. **Opening the Garage while holding the Water button or steering leaves the truck stuck spraying/steering.**
   - **Why it matters:** A toddler using two hands (one holding Water or dragging to drive, the other tapping the Garage button) will leave `fireTruck.spraying = true`, `waterButtonPointers` populated, or `steerPointerId` active when entering/exiting the Garage.
   - **Concrete fix:** Inside the `btnGarageEl.addEventListener('pointerdown', ...)` handler, explicitly reset input states when opening the garage:
     ```js
     steerPointerId = null;
     waterButtonPointers.clear();
     fireTruck.spraying = false;
     btnWaterEl.classList.remove('pressed');
     ```

3. **Camera and truck clip into hills and obstacles that lack collision entries or camera occlusion handling.**
   - **Why it matters:** The 4 hills (`hillPositions`) are not in `obstacles`, so the truck drives straight inside them and gets half-hidden; additionally, tall trees/houses/flames directly between the camera (`centerZ + 22.5`) and the truck (`centerZ`) block the child's view of their truck.
   - **Concrete fix:**
     - In Section 4 (`hillPositions.forEach`), register each hill in `obstacles` (`obstacles.push({ x: hp.x, z: hp.z, r: hp.r * 0.85, mesh: hm });`) OR flatten hills to walkable mounds and raise truck Y accordingly.
     - In `animate()` under `--- SMOOTH CAMERA FRAMING ---`, check distance from the camera-to-truck ray to `obstacles` and `activeFlames` (where `ob.z > fireTruck.z && Math.abs(ob.x - fireTruck.x) < 4.5 && ob.z - fireTruck.z < 18`) and either raise `desiredCamPos.y` by `+6` or fade the occluding mesh/flame materials.

4. **World boundary collision only nudges `fireTruck.angle += 0.6` while user drag immediately overrides it, pinning the truck against the fence.**
   - **Why it matters:** If the child keeps holding their finger toward the edge of the screen at the perimeter fence, the drag steering in `animate()` overwrites `fireTruck.angle` every frame, causing the truck to grind against the boundary and spam `playBoingSound()` every frame.
   - **Concrete fix:** In `animate()` at the `if (distFromCenter > WORLD_RADIUS)` check, push the position inward (`fireTruck.x = nx * (WORLD_RADIUS - 1.5); fireTruck.z = nz * (WORLD_RADIUS - 1.5);`), reflect the heading toward town (`fireTruck.angle = Math.atan2(nx, nz);`), and add a cooldown timer (`lastBoundaryBoing`) so `playBoingSound()` cannot fire more than once every `0.6` seconds.

5. **Parent 1's `tankerTruck` has no world-boundary or obstacle collision and can drive off the island forever.**
   - **Why it matters:** If a parent (or sibling) holds the gamepad stick in one direction, `tankerTruck.x` and `tankerTruck.z` grow unbounded, which also drags the shared camera (`centerX`, `centerZ`, `maxSpread`) away from the child's truck.
   - **Concrete fix:** In `animate()` under `--- PARENT 1 TANKER UPDATE & REFILL MOMENT ---`, clamp `tankerTruck` to `WORLD_RADIUS` (`const td = Math.hypot(tankerTruck.x, tankerTruck.z); if (td > WORLD_RADIUS) { tankerTruck.x *= WORLD_RADIUS / td; tankerTruck.z *= WORLD_RADIUS / td; }`) and run the same `obstacles.forEach` push-out loop used for `fireTruck`.

6. **Audio stays permanently silent on iOS Safari if the first touch is on a HUD button or if `AudioContext` starts in `'interrupted'` state.**
   - **Why it matters:** iOS Safari requires unlocking Web Audio and `speechSynthesis` inside a `touchend`/`pointerup` or `click` user gesture, and when returning from Siri/Home screen iOS sets `audioCtx.state` to `'interrupted'` (not just `'suspended'`), leaving the game completely mute for the toddler.
   - **Concrete fix:** In `initAudio()`, check `if (audioCtx && (audioCtx.state === 'suspended' || audioCtx.state === 'interrupted')) { audioCtx.resume().catch(()=>{}); }`, and attach `{ passive: true }` unlock listeners on `window` for both `pointerdown` and `pointerup`/`touchend` that call `initAudio()`.

7. **Spraying audio (`waterNoiseGain`) stays stuck on when opening the Garage while spraying.**
   - **Why it matters:** `handleWaterSpray()` checks `if (fireTruck.spraying && !isGarageOpen)`, stopping the water particles in the Garage, but `updateContinuousAudio()` is called with `fireTruck.spraying || tankerTruck.spraying || heli.spraying` without checking `!isGarageOpen`, so the loud white-noise spray hiss keeps playing inside the Garage.
   - **Concrete fix:** In `animate()`, change the `updateContinuousAudio` call to:
     ```js
     updateContinuousAudio(
       isGarageOpen ? 0 : fireTruck.speed / fireTruck.maxSpeed,
       !isGarageOpen && (fireTruck.spraying || tankerTruck.spraying || heli.spraying)
     );
     ```

8. **Unbounded `townFlowers` and un-pooled `rainbowArcs` leak Three.js geometries and materials over long play sessions.**
   - **Why it matters:** Every extinguished flame spawns 4–7 new `Mesh`/`MeshToonMaterial` flower objects into `townFlowers` (which is never capped) and creates 6 new `TorusGeometry` + `MeshBasicMaterial` objects in `spawnRainbowArc` without calling `.dispose()` when removed, eventually causing iPad Safari WebGL memory pressure and frame drops.
   - **Concrete fix:** In `spawnFlowerCluster()`, cap `townFlowers` at 80 items (`if (townFlowers.length > 80) { const old = townFlowers.shift(); scene.remove(old); }`) and share a single pre-built `flowerMaterials` map instead of calling `makeToonMat(col)` per flower; in `spawnRainbowArc()`, reuse shared `TorusGeometry` instances rather than allocating 6 new geometries per flame.