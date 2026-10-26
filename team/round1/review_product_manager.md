1. **BLOCKER: The hidden Garage overlay swallows touches on the Water and Siren buttons.**
   * **Why it matters:** A 3-year-old tapping the big glowing Water button gets zero response because `.garage-side-col` and `.garage-bottom-bar` have `pointer-events: auto` inside an `opacity: 0` parent, completely breaking the core spraying loop.
   * **Exact change:** In the `<style>` section, change `.garage-side-col` and `.garage-bottom-bar` to `pointer-events: none;`, and add `#garageOverlay.open .garage-side-col, #garageOverlay.open .garage-bottom-bar { pointer-events: auto; }` (or set `visibility: hidden` on `#garageOverlay` and `visibility: visible` on `#garageOverlay.open`).

2. **Colours look washed-out and pastel instead of candy-bright toy colors.**
   * **Why it matters:** Toddlers are drawn to bold, high-contrast, primary/candy colors (`#ff1f3d`, `#00a8ff`, `#2ed573`); washed-out lighting and pale house walls reduce visual delight and make the truck blend into the background.
   * **Exact change:** In section `3. THREE.JS SCENE`, lower `hemiLight` intensity from `0.78` to `0.45`, raise `dirLight` intensity from `0.72` to `1.1`, change `toonGradData` from `[145,145,145,255, 210,210,210,255, 255,255,255,255]` to `[95,95,95,255, 195,195,195,255, 255,255,255,255]`, thicken `outlineMat` default scale in `addOutline()` from `1.07` to `1.10`, and in `houseConfigs` replace the cream/pastel `wall` hexes (`0xfff6e5`, `0xeaf6ff`, etc.) with saturated candy colors (`0xffdd59`, `0x48dbfb`, `0xff9ff3`, `0x1dd1a1`).

3. **Trees, houses, and flames directly south (+Z) of the truck block the camera's view of the child's truck.**
   * **Why it matters:** When a 3-year-old loses sight of their fire truck behind a tree or giant flame, they lose spatial orientation and think the game is broken.
   * **Exact change:** In `animate()` under `--- SMOOTH CAMERA FRAMING ---`, raise the camera angle (`desiredCamPos.y` from `17.5` to `23.5` and `desiredCamPos.z` from `centerZ + 22.5` to `centerZ + 18.5`), and add a per-frame proximity check on `obstacles` and `activeFlames`: if any prop or flame is between the camera and `fireTruck` (`ob.z > fireTruck.z && ob.z < camera.position.z - 2 && Math.abs(ob.x - fireTruck.x) < 4.5`), smoothly scale it down or set `material.opacity = 0.35` (`transparent = true`).

4. **The truck can get stuck at the world perimeter or behind outer hills without being turned back toward town.**
   * **Why it matters:** A 3-year-old holding their finger in one spot will drive straight into the boundary or hills (`hillPositions`) and get trapped at the edge of the map.
   * **Exact change:** In `4. TOWN ENVIRONMENT`, add each hill in `hillPositions` to the `obstacles` array (`obstacles.push({ x: hp.x, z: hp.z, r: hp.r * 0.85, mesh: hm })`) and reduce `WORLD_RADIUS` from `54` to `42`. In `animate()` under `Soft world bounds`, instead of `fireTruck.angle += 0.6`, smoothly steer `fireTruck.angle` toward the town center (`Math.atan2(fireTruck.x, fireTruck.z)`) and push `fireTruck.x`/`z` inward by `2.5` units.

5. **Tapping and holding near the center of the screen drives the truck without steering it toward the child's finger.**
   * **Why it matters:** A 3-year-old naturally taps directly on or right next to the fire truck to make it go; because `steerAnchorX/Y` is hardcoded to the screen center, touches near the truck or when the camera is offset by co-op players steer in the wrong direction.
   * **Exact change:** In `animate()` under `--- CHILD FIRE TRUCK MOVEMENT & STEERING ---`, project `fireTruck.group.position` to 2D screen coordinates using `fireTruck.group.position.clone().project(camera)` and compute `dx = steerCurX - truckScreenX` and `dy = steerCurY - truckScreenY` (removing the `> 12` deadzone or lowering it to `> 4`) so the truck always drives directly toward the child's finger on screen.

6. **Parent 1's Water Tanker can drive off the island and through houses.**
   * **Why it matters:** When a parent joins on a controller or hands the controller to a sibling, driving through buildings or off the world edge breaks the shared toy-world illusion and pulls the shared camera away from the child.
   * **Exact change:** In `animate()` under `--- PARENT 1 TANKER UPDATE & REFILL MOMENT ---`, apply the exact same `WORLD_RADIUS` clamp and `obstacles` collision loop used for `fireTruck` to `tankerTruck.x` and `tankerTruck.z`, and clamp `tankerTruck` and `heli` positions to stay within `26` units of `fireTruck` so a parent controller never drags the camera off the 3-year-old.

7. **Once 3 kittens are rescued onto the ladder, kitten rescues never happen again for the rest of the session (and never persist).**
   * **Why it matters:** Saving the meowing kitty from a tree is the highest-delight moment in the game for a 3-year-old; permanently disabling it after 3 rescues kills replay value in longer play sessions.
   * **Exact change:** In `extinguishFlame()`, when `rescuedKittens.length >= 3` and a new kitten is rescued, make the oldest kitten on the ladder do a happy celebratory hop off the truck (or cycle its spot) so `spawnFlame(wantKitten)` can continue spawning kitten rescues indefinitely rather than capping at `rescuedKittens.length < 3`.

8. **Tapping the 3D duck, houses, trees, or the fire truck itself does nothing.**
   * **Why it matters:** 3-year-olds constantly poke objects in the toy world expecting immediate cause-and-effect delight ("tap the duck to make it quack and jump", "tap the truck to make it honk").
   * **Exact change:** In the `window.addEventListener('pointerdown', ...)` handler in section `9`, cast a `THREE.Raycaster` from the touch point against `[fireTruck.group, duckGroup, ...bouncyProps]`: if it hits `duckGroup`, trigger `playHornVariant('quack')` and a vertical hop; if it hits `fireTruck.group`, trigger `fireTruck.hopVel = 8` and the equipped horn; if it hits a tree or house in `bouncyProps`, trigger a squash-and-stretch bounce and `playBoingSound()`.