# Capture pitfalls

Each of these cost a run at least once.

## Selectors and clicks

- Two buttons share a name (a top-bar bell and a settings tab both called "Notifications"): filter by visible text (`locator('button').filter({ hasText: /^Notifications$/ })`), which icon buttons lack.
- Cards that are `div[role=button]` with nested controls open reliably by a mouse click at a position inside the body, not by `getByText`. A newly created card may need a reload before it opens.
- Never press Escape inside a modal you still need; it may close more than the popover.
- Native `confirm()` dialogs cannot be screenshotted: accept them with `page.on('dialog')`, log `d.message()`, and show the text as a note card.
- A file picker button opens the OS chooser: `Promise.all([page.waitForEvent('filechooser'), button.click()])`, then `setFiles`.
- Rich editors ignore `fill`; type with `page.keyboard.type`. Lists auto-continue on Enter, so do not type "- " again.
- "Click the last Delete button" is how real data gets deleted. Target the control by its accessible name, and check the database after any destructive step.

## State and sessions

- Saved storage state can hold a half-dead session: for auth journeys (sign out, reset) start from a fresh context and log in.
- Open tabs, drafts and panels often live in `localStorage`: a new browser context is not "after a reload". Test persistence with `page.reload()` in the same context.
- Writes made outside the app (SQL, admin APIs) skip cache invalidation: clear the framework data cache and restart before capturing.
- Out-of-band side effects (notifications, activity) are only produced by the UI path; seed through the API, act through the UI.

## Rendering

- Fixed 1440x900 viewport; boards scale every card to 16:10. For content below the fold, `scrollIntoViewIfNeeded()` the section and shoot the viewport.
- Install an emoji font and a fontconfig for headless Chromium, or emoji render as boxes.
- The hand-drawn Excalidraw font lacks some glyphs (ellipsis character, arrows, emoji); one missing glyph swaps the whole line's font. Use plain ASCII in card titles.
- A long capture session can exhaust the dev server heap; start it with a larger `--max-old-space-size` and watch the log.

## Safety in logs

- Dumps of URLs leak `#access_token`, `code=` and invite tokens. Strip query and hash before printing, and pipe script output through a redaction `sed` when a step touches auth.
