1. **Pinned `three.js` CDN script lacks Subresource Integrity (SRI) and `crossorigin` attributes.**
   - **Why it matters:** Without cryptographic hash verification on the only external network call, a compromised CDN or captive-portal injection on public Wi-Fi could execute arbitrary JavaScript or inject tracking/ads into a 3-year-old's browser session.
   - **Concrete change:** In `<head>` / before the main `<script>`, replace the `<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>` tag with:
     ```html
     <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" integrity="sha384-CI3ELBVUz9XQO+97x6nwMDPosPR5XvsxW2ua7N1Xeygeh1IxtgqtCkGfQY9WWdHu" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
     ```

2. **Missing Content Security Policy (CSP) `<meta>` tag to enforce zero unplanned network calls or external navigation.**
   - **Why it matters:** COPPA compliance and child safety require a hard browser-level guarantee that no third-party telemetry, WebSockets, or accidental external links can ever be triggered.
   - **Concrete change:** In `<head>`, add the following `<meta>` tag right after `<meta charset="UTF-8">`:
     ```html
     <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js; style-src 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'none'; media-src 'none'; frame-src 'none'; form-action 'none';">
     ```

3. **Unbounded and unvalidated `localStorage` deserialization in `1. PERSISTENCE & GARAGE STATE` can freeze the app or corrupt state.**
   - **Why it matters:** `parsed.stars` is not checked with `Number.isFinite()` (`NaN` or `Infinity` breaks star jar SVG math) and `parsed.unlocked[k]` arrays are not filtered against valid catalog IDs, meaning corrupted local storage can break the child's saved progress and lock up the UI.
   - **Concrete change:** In section `1. PERSISTENCE & GARAGE STATE`, replace the `try { const raw = ... } catch (e) {}` block with:
     ```javascript
     try {
       const raw = localStorage.getItem('splashTownSave_v1');
       if (raw && raw.length < 2048) {
         const parsed = JSON.parse(raw);
         if (parsed && Number.isFinite(parsed.stars)) {
           saveState.stars = Math.min(999, Math.max(0, Math.floor(parsed.stars)));
           ['paint','hat','sticker','horn','kitten'].forEach(k => {
             const validIds = new Set(GARAGE_CATALOG[k].map(it => it.id));
             if (Array.isArray(parsed.unlocked?.[k])) {
               const clean = parsed.unlocked[k].filter(id => Number.isInteger(id) && validIds.has(id));
               saveState.unlocked[k] = clean.includes(0) ? Array.from(new Set(clean)) : [0, ...new Set(clean)];
             }
             if (Number.isInteger(parsed.equipped?.[k]) && validIds.has(parsed.equipped[k]) && saveState.unlocked[k].includes(parsed.equipped[k])) {
               saveState.equipped[k] = parsed.equipped[k];
             }
           });
         }
       }
     } catch (e) {}
     ```
   *(Note: move `const GARAGE_CATALOG = ...` directly above this `try` block so `GARAGE_CATALOG` is defined when validating).*

4. **Dynamic `.innerHTML` assignments in `renderGarageItems()`, `getGarageItemSVG()`, `spawnRewardStarsFromWorldPos()`, and `registerChildTouch()`.**
   - **Why it matters:** Constructing DOM nodes via `.innerHTML` with template literals (`${item.color}`, `${hex}`) violates our strict no-dynamic-`innerHTML` security rule and creates an XSS sink if catalog or state data is ever extended.
   - **Concrete change:** Add a safe SVG parser helper using `DOMParser` in section `10. STAR GARAGE UI & INTERACTION` and replace `.innerHTML` assignments in `renderGarageItems()`, `spawnRewardStarsFromWorldPos()`, and `registerChildTouch()`:
     ```javascript
     function setSafeSVG(container, svgString) {
       container.textContent = '';
       if (!svgString) return;
       const doc = new DOMParser().parseFromString(svgString, 'image/svg+xml');
       const svg = doc.querySelector('svg');
       if (svg) container.appendChild(document.importNode(svg, true));
     }
     ```
     Then in `renderGarageItems()`, replace `wrap.innerHTML = '';` with `wrap.textContent = '';`, `btn.innerHTML = getGarageItemSVG(cat, item);` with `setSafeSVG(btn, getGarageItemSVG(cat, item));`, `lock.innerHTML = ...` with `setSafeSVG(lock, ...)`, and `costRow.innerHTML = starsSvg;` with a loop calling `setSafeSVG`. Do the same for `el.innerHTML` in `spawnRewardStarsFromWorldPos()` and `sp.innerHTML` in `registerChildTouch()`.

5. **Hidden `#garageOverlay` child containers (`pointer-events: auto`) intercept touch events over the HUD (`#btnWater` / `#btnSiren`) when the overlay is closed.**
   - **Why it matters:** Because `.garage-side-col` and `.garage-bottom-bar` set `pointer-events: auto` while `#garageOverlay` only sets `pointer-events: none` and `opacity: 0` when closed, the invisible garage bars hijack the 3-year-old's touches on the Water button (Playtest Blocker #1) and allow blind unlocking/spending of stars while the overlay is hidden.
   - **Concrete change:** In `<style>`, update `.garage-side-col` and `.garage-bottom-bar` so they only accept pointer events when `#garageOverlay.open` is active:
     ```css
     #garageOverlay:not(.open) {
       visibility: hidden;
     }
     .garage-side-col, .garage-bottom-bar {
       pointer-events: none;
     }
     #garageOverlay.open .garage-side-col,
     #garageOverlay.open .garage-bottom-bar {
       pointer-events: auto;
     }
     ```

6. **`window.speechSynthesis` in `speakCue()` can use remote/cloud-backed OS voices and is not persisted when parents mute the game.**
   - **Why it matters:** On iPadOS/Chrome, default `SpeechSynthesis` voices can route text cues to cloud TTS servers if a local voice isn't explicitly selected, and muting via the parent control (`#muteZone`) is lost on page reload, unexpectedly speaking aloud.
   - **Concrete change:** In `speakCue(text)`, force a `localService === true` voice if available, and persist `isMuted` in `saveState`:
     ```javascript
     const voices = window.speechSynthesis.getVoices();
     const localVoice = voices.find(v => v.lang.startsWith('en') && v.localService);
     if (localVoice) u.voice = localVoice;
     ```
     And in `defaultSave` (section 1), add `muted: false`, read `isMuted = !!parsed.muted;` on load, and save `saveState.muted = isMuted; persistState();` inside the `muteZone` `pointerdown` timeout.