# Tasklet · Use-case catalog

Example output of the mapping-product-flows skill on a fictional app.

- **Base:** static demo pages in `examples/demo/app`, captured with `examples/demo/capture.mjs`.
- **Personas:** Ana Lima (owner), Rui and Bruno (members), all at Northwind Bakery.
- **Out of scope:** billing, admin.

**States**

- 🟢 **In production:** what a production user sees today.
- 🟡 **Behind a flag:** in the code, flag off in production.
- 🟣 **Hidden in the UI:** works, but no screen leads to it.
- ⚪ **Outside the app:** e-mail, identity provider, desktop.

**Product size:** 6 use cases, 14 screens, 2 e-mails, 2 third-party steps, 2 area boards.

| Board | Area | Use cases | Screens |
|---|---|---|---|
| `01-access.excalidraw` | Access and account | 4 | 8 |
| `02-tasks.excalidraw` | Tasks | 2 | 6 |

---

## 01 · Access and account

_Tasklet, a fictional to-do app for small teams. Persona Ana Lima (Northwind Bakery) signs up, signs in with Lumen ID (a fictional identity provider), and fails a sign-in. Static demo pages, captured with Playwright._

**UC-ACC-01 · Create an account with e-mail** 🟢
Work e-mail and password (at least 8 characters). Tasklet sends a confirmation link; the link opens the team space.
Steps: 1. Sign up → 2. Password too short (Create account): "Password must be at least 8 characters." → 3. Check your e-mail (fixes it) → 4. Confirmation e-mail (e-mail) [e-mail]: From noreply@tasklet.example. → 5. Team space (Confirm my e-mail)

**UC-ACC-02 · Sign in with Lumen ID** 🟢
"Continue with Lumen ID" opens the provider's account chooser. Choosing the account returns to the team space.
Steps: 1. Sign up → 2. Choose an account (Continue with Lumen ID) [loose end]: Says "to continue to auth.tasklet-infra.example", not Tasklet. → 3. Consent (Ana Lima) [third party]: A real provider account is needed past this point; not capturable. → 4. Team space (callback)

**UC-ACC-03 · Sign in and get the password wrong** 🟢
E-mail and password. A wrong password shows a generic error that does not say which field is wrong.
Steps: 1. Sign in → 2. Wrong password (Sign in): "Incorrect e-mail or password."

**UC-ACC-04 · Variation: reset a forgotten password** 🟢
The sign-in page offers "Forgot password?". The link leads nowhere.
Steps: 1. Sign in → 2. 404 (Forgot password?) [loose end]: No reset page exists.

**Loose ends in this area**

• Lumen ID shows the infrastructure domain auth.tasklet-infra.example instead of the app name (configure the provider's app name and a branded auth domain).
• "Forgot password?" leads to a 404: there is no way to recover an account.

---

## 02 · Tasks

_Northwind Bakery's team space in Tasklet, as Ana Lima. Five seeded tasks spread over overdue, this week, later and no date so every filter has results._

**UC-TSK-01 · Create a task and assign it** 🟢
New task asks for title, due date and assignee. The task appears at the top of the list and the assignee gets an e-mail.
Steps: 1. Tasks → 2. New task (New task) → 3. Created (Create task): "Task created and assigned to Rui". → 4. E-mail to Rui (e-mail) [e-mail]: "Ana assigned you a task".

**UC-TSK-02 · Filter tasks by due date** 🟢
Chips filter the list: all, due this week, overdue, assigned to me. The filter lives in the URL, so a filtered view can be shared.
Steps: 1. All → 2. Due this week (Due this week) → 3. Overdue (Overdue) → 4. Empty filter (shared link): "No tasks here."

---

## Loose ends, by severity

| Severity | Finding |
|---|---|
| medium | "Forgot password?" leads to a 404: an account that loses its password cannot be recovered (UC-ACC-04). |
| low | The identity provider shows auth.tasklet-infra.example instead of Tasklet on the account chooser (UC-ACC-02). |
