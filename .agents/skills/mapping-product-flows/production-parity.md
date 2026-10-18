# Production parity checklist

Every item below produced a wrong screen at least once when skipped. Do all of them before the first capture, and re-check after any restart.

## 1. Feature flags

- List the flag **names** set in production without pulling values (Vercel: `vercel env ls production --project <p> --scope <team>`; other hosts: their env listing). A name present usually means on; confirm against feature records or a recent release note.
- Read each flag's resolver. Defaults that depend on the environment are the trap: code like `default = env !== 'production'` turns features ON locally that production does not have. Pin every flag explicitly: production's set to on, everything else to `off`.
- Flags that transform the frontend (navigation, a frame around a page, a sidebar) change every screenshot in that area. Capture with production's set; capture flag-off features on a second server or after, and mark them 🟡.
- Note the access-mode and rate-limit settings of internal APIs used for seeding; open them locally only (canary modes and rate limits are not user-visible).
- **Flag-off features:** if flags are read at runtime (`process.env` on the server), start a second server on another port from the same build and database with those flags on. Cookies ignore the port, so saved sessions work on both. Point the capture lib at it with `FLOWMAP_BASE`. Check each flag's real footprint in code first: some only change chips inside documents, not the board.
- Read each flagged feature's FDR/ADR status (Draft, Active) and write it on the board.

## 2. Database privileges

A database built only from migrations can lack grants that production has (historical default privileges no migration reproduces). Symptom: notifications, favorites, notes, chat threads or layouts silently empty, because many clients return `{ error }` instead of throwing.

```sql
select r.rolname, c.relname,
  has_table_privilege(r.oid, c.oid, 'SELECT') s, has_table_privilege(r.oid, c.oid, 'INSERT') i,
  has_table_privilege(r.oid, c.oid, 'UPDATE') u, has_table_privilege(r.oid, c.oid, 'DELETE') d
from pg_class c join pg_namespace n on n.oid = c.relnamespace cross join pg_roles r
where n.nspname = 'public' and c.relkind in ('r','v','m') and r.rolname in ('anon','authenticated','service_role');
```

Run it read-only on production (management API) and locally; generate GRANTs for the difference and apply them locally in one transaction. Re-run until zero differences. Report the drift as a finding: a fresh environment would break the same way.

## 3. Background workers

Previews, thumbnails, text extraction and AI descriptions usually come from workers or crons that do not run locally. Without them every file shows "generating".

- Prefer the repo's own e2e stubs; check which formats they refuse (a stub may accept only PDF because CI lacks LibreOffice).
- Run the worker **inside the production decoder image** when one exists locally (`podman images`), mounting the worktree read-only with host networking. Keep any patched copy outside the repo.
- Trigger crons with the local cron secret; repeat until the queue is empty. Requeue jobs that failed before the worker existed.

## 4. AI features

Point the app's AI base URL at an available gateway with a model of the same family as production's default, so answers look like production's. Use a cheap, non-quota model when possible. Verify one real answer in the database before capturing.

## 5. E-mail and auth flows

- If the local auth server has no mail catcher, run one on the stack's network with the hostname it expects (Supabase: `mailpit` image, `--network-alias supabase_inbucket_<project>`). Then reset and confirmation flows run for real and the link comes from the caught e-mail.
- The local auth server's own templates are its defaults: use the caught e-mail only for the link, and render the production template for the board.
- Local redirect allow-lists and `localhost` vs `127.0.0.1` can break the last hop of a callback; correct the host in the script and record it as local-only.
- **OAuth connectors you host** (an MCP or API that Claude or others sign in to): build a real authorize URL with the client's own metadata document and PKCE, capture the consent screen, approve, exchange the code as the client would, and show where the connection appears and how to disconnect it.

## 6. Local-only differences to record, not fix

E-mail sending off (log shows "would have sent"), e-mail confirmation off in the local auth config, canary API modes. Show the real artifact (template, provider screen) instead.

## 7. Safety

- Read-only on production: aggregates and privilege checks only, no personal data.
- Stop local servers by PID after checking their working directory; other sessions run servers too.
- Any third-party package you install: inspect it first (version age, repository, install scripts) and install into an isolated directory with `--ignore-scripts`.
