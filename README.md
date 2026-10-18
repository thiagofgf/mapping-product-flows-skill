# Mapping Product Flows Agent Skill

A portable [Agent Skill](https://agentskills.io/specification) that maps every
user journey of a web app end to end and turns it into Excalidraw boards and
PNGs: one board per product area, one lane per use case, real screenshots
joined by arrows labelled with the exact button text, plus the e-mails, OAuth
and third-party screens the journey passes through.

It answers "how big is our product?" with numbers (use cases, screens,
e-mails, third-party steps) and finds the loose ends along the way, each one
verified before it is written down.

Nothing about a particular product is hard-coded. The skill walks the app the
way production runs it: production feature flags, production database
privileges, the real background workers, fictional data seeded through the
app's own APIs.

## Skills

- `mapping-product-flows`: inventory the use cases, make the local app match
  production, seed personas, capture every journey, draw the boards, verify
  findings and generate the use-case catalog.

## What you get

- `00-overview` board: totals, one tile per area with its use cases, and the
  findings ranked by severity.
- One board per area (`01-access`, `02-home`, …) with a lane per use case,
  alternative flows and failures in their own lanes, and the area's findings.
- A board for features behind flags that are off in production, captured on a
  second server.
- A Markdown catalog generated from the same specs, so codes and wording never
  drift from the boards.

Labels default to English; set `"lang": "pt"` in a spec for Portuguese.

## Install

### Codex

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo thiagofgf/mapping-product-flows-skill \
  --path .agents/skills/mapping-product-flows
```

### Claude Code

```bash
git clone https://github.com/thiagofgf/mapping-product-flows-skill.git ~/.local/share/mapping-product-flows-skill
mkdir -p ~/.claude/skills
ln -s ~/.local/share/mapping-product-flows-skill/.agents/skills/mapping-product-flows ~/.claude/skills/mapping-product-flows
```

### Repository-local agents

Copy `.agents/skills/mapping-product-flows` into the repository. For Claude
Code compatibility, link `.claude/skills` to `../.agents/skills`.

## Requirements

- Python 3.10+ (board, index and catalog generators; standard library only).
- Node.js with [Playwright](https://playwright.dev/) available in the app's
  repository, for `tools/capture-lib.mjs`.
- [`mcp-excalidraw-server`](https://github.com/yctimlin/mcp_excalidraw) for
  rendering boards to PNG:
  `npx mcp-excalidraw-server render board.excalidraw --out board.png`.
- A local, production-like build of the app you are mapping.

## Layout

```text
.agents/skills/
└── mapping-product-flows/
    ├── SKILL.md                 workflow, deliverables, how to verify a finding
    ├── production-parity.md     flags, database privileges, workers, e-mail and auth
    ├── capture-pitfalls.md      selectors, sessions, rendering, safe logs
    ├── tools/
    │   ├── extract_controls.py  UI control inventory from a source tree
    │   ├── capture-lib.mjs      Playwright sessions, one screenshot per step
    │   ├── build_board.py       area board from a JSON spec
    │   ├── build_index.py       overview board
    │   └── gen_md.py            use-case catalog from the specs
    └── examples/
        ├── board-spec.json
        └── catalog-header.md
.claude/skills -> ../.agents/skills
```

`.agents/skills` is the only canonical source; the Claude path is a symlink so
the skill definition cannot drift.

## License

Distributed under the [MIT License](LICENSE).
