---
name: mapping-product-flows
description: Use when asked to map every user flow, journey, screen or use case of an app (product sizing, flow map, journey inventory, "all use cases end to end"), especially when emails, OAuth or third-party logins must appear, and the result is diagrams such as Excalidraw files and PNGs.
---

# Mapping product flows

## Overview

A flow map is only worth what its screens are: **every node is a screenshot of the real app, running locally the way production runs it, with fictional data.** Mockups drawn from code agree with the code and still lie about the product. Walking the real app also finds the loose ends, which are half the value, and every loose end is verified before it is written down.

## When to use

- "Map all flows / screens / use cases", "how big is the product", journey inventory.
- Needs emails, OAuth/Google, invites, notifications on the map.
- Not for: one diagram of one feature, architecture diagrams, admin consoles the user excluded.

## Deliverables

1. **One Excalidraw + PNG per area** (Access, Team, Home, Files, Boards, Card, Projects, Cycles, AI, Settings…). One lane per use case `UC-AREA-NN`: header with code, description and state; then screenshot cards joined by arrows labelled with the **exact button text**. Variations and failures get their own lane, never a card chained after the happy path's last step.
2. **An index board** (`00-…`): totals (use cases, screens, emails, third-party screens, boards), one tile per area with its use-case list, legend, and the findings ranked by severity. This is the "size of the product".
3. **A board for features behind flags that are off in production**, captured on a second server (see parity).
4. **Use-case catalog (Markdown)** generated from the board specs with `tools/gen_md.py`, so codes and wording never drift from the boards. A hand-written draft before capture is fine for planning; regenerate it at the end.
5. **Findings**: each with `file:line`, how it was verified, and production evidence when it exists. The ones the user confirms become tracker cards in their format.

States: 🟢 production · 🟡 behind a flag off in production · 🟣 hidden in the UI, reachable only by link · ⚪ outside the app.

## Workflow

1. **Current code.** `git fetch`; capture from a fresh worktree at `origin/main`.
2. **Inventory from the UI, not the routes.** `tools/extract_controls.py <app source dir> [out.json]` (aria-label, title, placeholder, button text per component), cross-checked with feature records (FDR/ADR), email templates, notification kinds and flags. A use case is a complete action (filter a board by due date; mention someone until the e-mail arrives), not a screen. Check whether a whole area is deliberately hidden from navigation before mapping it as a journey.
3. **Make local look like production.** Do every check in [production-parity.md](production-parity.md).
4. **Seed a believable world through the app's own APIs**, several personas with different roles plus one outsider; dates spread so every filter has results; real files so previews render. Do UI-only side effects (notifications, activity) through the UI during capture.
5. **Capture** with `tools/capture-lib.mjs` (env-configured; `step()` keeps a journey going past one broken selector). Read [capture-pitfalls.md](capture-pitfalls.md) before the first script.
6. **Outside the app, capture the real thing**: OAuth provider authorize pages, connector consent screens, auth e-mails from the provider's production templates, app e-mails rendered from the repo with fictional props, all framed in a neutral mail reader. Steps that need a real third-party account are dashed "not capturable" cards.
7. **Verify every finding before writing it** (see below).
8. **Draw** with `tools/build_board.py` (spec format in its docstring; a minimal one is in `examples/`), the index with `tools/build_index.py`, the catalog with `tools/gen_md.py`. Set `"lang": "pt"` in a spec for Portuguese labels; English is the default. **Render and look** at every PNG (`mcp-excalidraw-server render file.excalidraw --out file.png`); fix truncated labels, arrows into the wrong card, glyphs the hand-drawn font lacks.
9. **Deliver** files where the user reads them; say what is 🟡, 🟣 and ⚪, and what differs only locally.

## Verifying a finding

| Looks like a bug | Before writing it |
|---|---|
| A screen shows an error | Read the server log, then the DB: often the write succeeded and only the render failed (that is the finding) |
| Something "doesn't save" | Query the row; then rule out your own automation (Enter submitting, `fill` not firing input events) |
| Login/logout loops, missing session | Reproduce in a **fresh** browser context: if it repeats there it is real, if not it was the saved storage state |
| Wrong date or count | Find the write and the formatter in code, then prove it through the UI with a second value |
| Affects production? | Same code on current `origin/main`, then a read-only aggregate, an error-tracker search, or a harmless GET to production |
| Model answered oddly | Note it as an observation unless the context sent to the model is shown to be the cause |

## Common mistakes

| Mistake | Fix |
|---|---|
| Placeholder for Google/OAuth | Capture the live authorize page; it is often a finding |
| Rendering the default auth e-mail | Fetch the production template and subject from the provider |
| Trusting a flag default | Pin every flag; capture flag-off features on a second server |
| Admin `generate_link` for password reset | It skips PKCE; request the reset through the app and read the caught e-mail |
| Full-page screenshots on the board | Cards are a fixed 16:10; scroll the target into view instead |
| `pkill -f <server>` | Kill by PID after checking `/proc/<pid>/cwd` and the env |
| Printing tokens in dumps | Never dump auth URLs, `#access_token`, codes or PATs; redact in every log line |
| Exit code 0 = done | Read the output; a 0 can hide "skipped" |

## Loose ends to hunt

Defined-but-never-produced notification kinds; preferences promising things that never fire; errors swallowed (`try/catch` around clients that return `{error}`); dates written as UTC midnight and shown in local time; work done during render (cache revalidation, cookie writes); gates that also block invite links; whole areas with no way back in; URLs or slugs that break on accents; stale copy or old brand domains in templates; third-party screens showing infrastructure names; first screens that send new users the wrong way; suggestion chips that promise tools the AI does not have.
