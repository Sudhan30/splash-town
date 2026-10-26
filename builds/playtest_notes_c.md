Human playtest of this build in Chrome (desktop, touch emulated with pointer events):
1. BLOCKER: the hidden Garage overlay's bottom bar (#garage-bottom-bar) sits on top of the WATER button and swallows
   its touches, so the child cannot spray at all while the garage is closed. Hidden overlays must not receive input
   (display:none or pointer-events:none when closed).
2. Colours still look pale/pastel and washed out, not bold and saturated (too much ambient/hemisphere light, low-chroma
   palette, toon ramp too bright). Target: candy-bright, high-chroma, strong contrast, dark outlines.
3. A flame on a tree directly in front of the truck hides the truck from the camera; the camera should keep the truck
   visible (raise/pull back or fade occluders).
4. In another build of the same game, the truck drove into the fence corner and got stuck half-hidden behind a hill,
   with the camera very close; make sure world edges push the truck back toward the town and the camera never clips.
5. The tutorial hand worked; driving worked (hold and drag); flames with faces and the target ring worked.
