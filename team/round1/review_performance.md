1. **Full Retina 2x pixel ratio with MSAA andInverted-Hull outlines exceeds fill-rate on older iPad GPUs.**
   * **Why it matters:** Rendering 2048×1536 pixels with 4x MSAA and double-drawn outlined geometry causes severe thermal throttling and drops frame rates to 20–30 FPS, making touch steering feel sluggish for a 3-year-old.
   * **Concrete change:** In section `3. THREE.JS SCENE` and inside `onResize()`, clamp the pixel ratio to `1.25` instead of `2`:
     ```js
     renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.25));
     ```

2. **Unbounded flower spawning and per-frame scaling/rotation of all flowers degrades frame time over a play session.**
   * **Why it matters:** Every extinguished flame adds 4 to 7 new `Group`s, `Mesh`es, and `MeshToonMaterial`s to `townFlowers` without ever removing old ones; after 15–20 fires, CPU draw-call overhead and scene-graph traversal cause progressive stutter during long play sessions.
   * **Concrete change:** In section `4. TOWN ENVIRONMENT` (around `spawnFlowerCluster`), pre-create a shared palette of 5 `MeshToonMaterial`s (`const flowerMats = flowerCols.map(c => makeToonMat(c));`), cap `townFlowers` at `60` by reusing the oldest flower group when `townFlowers.length >= 60`, and in `animate()`, skip `MathUtils.lerp` and `setScalar` once `Math.abs(fl.scale.x - fl.userData.targetScale) < 0.01`.

3. **Dynamic geometries and materials are allocated and leaked every time a flame, rainbow arc, kitten, or garage hat/sticker is created.**
   * **Why it matters:** Repeatedly instantiating `ConeGeometry`, `PlaneGeometry`, `RingGeometry`, `TorusGeometry`, and `MeshToonMaterial` without `.dispose()` leaks WebGL buffers in Safari and triggers garbage collection pauses right when a flame is extinguished (the reward moment).
   * **Concrete change:**
     * In section `7. SILLY CARTOON FLAMES` (`spawnFlame`), hoist `outerGeo`, `innerGeo`, `facePlane` geometry, `ringGeo`, `innerMat`, `ringMat`, and the 2 `outerMat`s (normal and family) outside `spawnFlame` as module-level shared constants.
     * In section `8. POOLED PARTICLES` (`spawnRainbowArc`), hoist the 6 `TorusGeometry` and `MeshBasicMaterial` instances outside `spawnRainbowArc` so the function only creates Meshes referencing shared assets.
     * In `applyGarageCustomizationsToTruck()`, dispose old child geometries/materials before `remove()`, or pre-build the 6 hat groups and 4 sticker meshes once at startup and toggle `.visible`.

4. **160 individual transparent `Mesh` objects in the particle pool generate up to 160 separate draw calls and sorting passes during water spraying and confetti bursts.**
   * **Why it matters:** Spraying water into a flame while confetti bursts spikes draw calls and alpha overdraw simultaneously, causing the celebration moment to stutter right when the child and parents splash together.
   * **Concrete change:** In section `8. POOLED PARTICLES`, reduce the pool size from `160` to `80`, replace `particles.find(item => !item.active)` in `emitParticle` with a ring-buffer index (`let nextParticleIdx = 0; const p = particles[nextParticleIdx = (nextParticleIdx + 1) % particles.length];`), and set `partGeo = new THREE.SphereGeometry(0.28, 5, 4)` (40 triangles instead of 128 per particle).

5. **Per-frame object allocations (`new THREE.Vector3`, `Array.from`, `.filter`) inside `animate()` and `pollGamepads()` cause regular GC micro-stutters.**
   * **Why it matters:** Allocating temporary vectors and arrays 60 times a second triggers Safari's garbage collector every few seconds, causing visible hitches while driving.
   * **Concrete change:**
     * In `animate()` under `--- SMOOTH CAMERA FRAMING ---`, replace `new THREE.Vector3` calls with two pre-allocated module-scope vectors (`const _camOffset = new THREE.Vector3(); const _desiredCamPos = new THREE.Vector3();`) updated via `.set(...)`.
     * In `pollGamepads()`, remove `Array.from(navigator.getGamepads()).filter(Boolean)` and index the raw `Gamepads` list directly (`const rawPads = navigator.getGamepads(); const pad0 = rawPads && rawPads[0]; const pad1 = rawPads && rawPads[1];`).

6. **46 fence groups (92 meshes) and 14 cloud groups (~56 high-poly spheres) add ~150 unnecessary draw calls every frame.**
   * **Why it matters:** Static perimeter fences and background clouds consume nearly half the WebGL draw-call budget on an older iPad before any interactive toys or particles are drawn.
   * **Concrete change:**
     * In section `3. THREE.JS SCENE` (clouds loop), reduce `puffGeo` segments from `(1, 12, 10)` to `(1, 7, 5)` and cloud count from `14` to `8`.
     * In section `4. TOWN ENVIRONMENT` (fence loop), replace the 46 `THREE.Group`s with two `THREE.InstancedMesh` instances (`new THREE.InstancedMesh(fencePostGeo, fenceMat, fenceCount)` and `new THREE.InstancedMesh(fenceRailGeo, fenceMat, fenceCount)`), reducing 92 draw calls to 2.

7. **CSS `backdrop-filter: blur(8px)`, `filter: drop-shadow(...)`, and hidden garage child `pointer-events: auto` hurt compositor performance and block touch input.**
   * **Why it matters:** Real-time Gaussian blur over a live WebGL canvas is extremely expensive on older iPad tile-based GPUs, `drop-shadow` on animated Tutorial/Star DOM nodes forces rasterization every frame, and `.garage-side-col` / `.garage-bottom-bar` having `pointer-events: auto` while `#garageOverlay` is only `opacity: 0` swallows touches on the Water button (Playtest Blocker #1).
   * **Concrete change:**
     * In `<style>`, add `visibility: hidden;` to `#garageOverlay` and `visibility: visible;` to `#garageOverlay.open` (so hidden child bars cannot intercept touches or incur compositor cost).
     * Remove `backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);` from `.garage-side-col` and `.garage-pill`, using a solid semi-opaque background `background: rgba(20, 60, 120, 0.88);` instead.
     * Add `display: none;` to `#tutorialHand.hidden` so its two `infinite` keyframe animations and `filter: drop-shadow(...)` stop running on the compositor while hidden.