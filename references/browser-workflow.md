# Browser workflow for Lanhu/Axure canvases

Read this reference only for a live prototype link. Browser APIs and confirmation rules come from the browser-control skill; this file records the Lanhu-specific mechanics that avoid missed regions and mismatched text.

## Identify the rendered canvas

After selecting the matching signed-in tab, inspect a DOM snapshot and locate the Axure iframe. Current Lanhu pages commonly use `#lan-mapping-iframe`, but verify rather than assuming. A strong candidate has a visible, large rectangle and an `axure-file.lanhuapp.com` URL.

Use a frame-scoped read to record:

- `document.documentElement.scrollWidth` and `scrollHeight` — native canvas size at the current zoom.
- `innerWidth`, `innerHeight`, `scrollX`, and `scrollY` — current iframe viewport.
- `body.innerText` — prototype text corresponding to the rendered canvas.

Record the outer iframe rectangle as well. Review comments normally live in the outer Lanhu document, not the Axure frame.

## Preferred capture: temporary full-canvas rendering

Use a disposable same-session tab so temporary layout changes never touch the user's working tab.

1. Open the exact source URL in the disposable tab and wait for the selected prototype page to render.
2. When native dimensions materially exceed the normal viewport, temporarily request a large browser viewport. Respect the backend limit; 4096 × 4096 is commonly sufficient as a staging viewport.
3. On this fresh tab, read the CDP capability documentation before using it.
4. Call `Page.getFrameTree` and select the child frame by verified frame name or URL.
5. Call `Page.createIsolatedWorld` for that frame. Read its document dimensions through `Runtime.evaluate` in the returned execution context.
6. In the disposable tab's main document, temporarily:
   - set overflow to visible on the iframe and its ancestors;
   - size `html` and `body` to the measured canvas;
   - place the iframe at `(0, 0)` with the measured width and height, no border, and a top stacking order.
7. Confirm in the child execution context that `innerWidth` and `innerHeight` now equal the measured canvas dimensions.
8. Wait briefly for repaint, take a full-page PNG screenshot, and verify its pixel dimensions equal the canvas dimensions.

This technique renders the cross-origin Axure frame at its native size before capture. It is more reliable than wheel-scrolling because it removes scroll targeting, acceleration, and stitching errors.

Close the disposable tab after exporting. If it must remain open, restore every changed style and report the temporary page-state modification.

## Fallback: exact frame scrolling

Use this when a single full-canvas screenshot exceeds browser image limits or fails to render.

1. Keep all work in the disposable tab.
2. Choose a tile viewport that fits inside the visible iframe.
3. Build row and column origins that cover `(0, 0)` through the final canvas edge with overlap.
4. In the iframe's isolated execution context, call `scrollTo(x, y)` for each origin.
5. Read back `scrollX` and `scrollY`; do not assume the requested values were accepted near an edge.
6. Capture only the iframe rectangle or the intended tile rectangle after each verified scroll.
7. Name files by row and column and write the verified origin into the manifest.

Prefer exact frame scrolling over synthetic wheel input. Wheel events can hit Lanhu's outer document or side panels instead of the Axure document.

## Text and comments

Export iframe `body.innerText` without trying to infer spatial grouping from DOM order alone. Screenshots remain authoritative for layout, arrows, callouts, modal relationships, and visual states.

For comments, use the visible outer comment container when present and state that the export contains currently loaded comments. Do not claim completeness if the list is paginated, filtered, collapsed, or lazily loaded.

## Failure handling

- Authentication expired: ask the user to sign in in the selected browser.
- Canvas still loading: wait for a stable size and representative text/image content before capture.
- Screenshot dimensions mismatch: do not split it; correct the iframe sizing or use exact scrolling.
- Cross-origin access blocked through page JavaScript: use the documented frame locator or CDP isolated world; do not inspect cookies or session storage.
- Extremely large or sparse canvas: keep complete coverage by default. Offer content-aware trimming only as a separate, clearly disclosed derivative.
