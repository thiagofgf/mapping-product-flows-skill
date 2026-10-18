# <Product> · Use-case catalog

Flow map of the app, walked end to end with fictional data.

- **Base:** `origin/main` <sha> (<date>), local production build, production flags.
- **Personas:** <owner>, <admin>, <members>, <one outsider>.
- **Out of scope:** <what the user excluded>.

**States**

- 🟢 **In production:** what a production user sees today.
- 🟡 **Behind a flag:** in the code, flag off in production; captured with it on for the map.
- 🟣 **Hidden in the UI:** works, but no screen leads to it; link only.
- ⚪ **Outside the app:** e-mail, OAuth provider, desktop; shown with the real artifact.

**Flags that change the screen**

| Flag | Production | What changes for the user |
|---|---|---|
