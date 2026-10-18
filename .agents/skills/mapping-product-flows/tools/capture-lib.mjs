// Shared capture helpers for a flow map: persona sessions, one screenshot per step, failure diagnostics.
// Configure with env vars (no edits needed for the generic parts):
//   FLOWMAP_PKG   package.json of a project that has `playwright` installed (the app's own repo works)
//   FLOWMAP_BASE  app origin, e.g. http://127.0.0.1:3417 (a second server with other flags just changes this)
//   FLOWMAP_DIR   work dir: <dir>/seed/state.json (personas + ids), <dir>/auth/<persona>.json, <dir>/shots/<journey>/
//   FLOWMAP_WS    path prefix that s.go('?view=x') appends to, e.g. /workspace/my-team
//   FLOWMAP_DUMP_HIDE optional regex of control lines to drop from dumps (e.g. the top navigation). Off by default:
//                 a hidden line is a hidden screen, which is how a whole menu entry was once missed.
// login() below is app-specific: adapt it once per product (gate password, email + password form).
import { createRequire } from 'node:module'
import fs from 'node:fs'
const require = createRequire(process.env.FLOWMAP_PKG || process.cwd() + '/package.json')
export const { chromium } = require('playwright')
export const BASE = process.env.FLOWMAP_BASE || 'http://127.0.0.1:3000'
const DIR = process.env.FLOWMAP_DIR || '/tmp/flowmap'
export const WS = BASE + (process.env.FLOWMAP_WS || '')
const STATE = fs.existsSync(`${DIR}/seed/state.json`) ? JSON.parse(fs.readFileSync(`${DIR}/seed/state.json`, 'utf8')) : { people: {} }
export const PEOPLE = STATE.people
export const SEED = STATE

export async function session(journey, persona = 'Marina', opts = {}) {
  const out = `${DIR}/shots/${journey}`
  fs.mkdirSync(out, { recursive: true })
  const browser = await chromium.launch()
  const authFile = `${DIR}/auth/${persona}.json`
  const ctx = await browser.newContext({
    viewport: opts.viewport ?? { width: 1440, height: 900 }, locale: 'en-US', timezoneId: 'America/Sao_Paulo',
    ...(persona && fs.existsSync(authFile) && !opts.fresh ? { storageState: authFile } : {}),
  })
  const page = await ctx.newPage()
  page.setDefaultTimeout(15000)
  const steps = fs.existsSync(`${out}/steps.json`) && opts.append ? JSON.parse(fs.readFileSync(`${out}/steps.json`)) : []
  const s = {
    browser, ctx, page, out, steps,
    async login(who = persona) {
      await page.goto(BASE + '/beta')
      if (page.url().includes('/beta')) {
        await page.fill('input[name=password]', process.env.FLOWMAP_GATE_PASSWORD || ''); await page.click('button[type=submit]')
        await page.waitForURL(u => !u.pathname.startsWith('/beta'))
      }
      if (!page.url().includes('/login')) await page.goto(BASE + '/login')
      if (page.url().includes('/login')) {
        await page.fill('input[type=email]', PEOPLE[who].email)
        await page.getByRole('button', { name: 'Sign In With Email' }).click()
        await page.fill('input[placeholder="Password"]', PEOPLE[who].password)
        await page.click('button[type=submit]')
        await page.waitForURL(u => u.pathname.startsWith('/workspace/') || u.pathname === '/onboarding', { timeout: 30000 })
      }
      fs.mkdirSync(`${DIR}/auth`, { recursive: true }); await ctx.storageState({ path: `${DIR}/auth/${who}.json` })
    },
    async go(path) { await page.goto(path.startsWith('http') ? path : WS + path); await settle() },
    async shot(id, title, extra = {}) {
      await settle(extra.wait ?? 700)
      const file = `${out}/${id}.png`
      if (extra.locator) await extra.locator.screenshot({ path: file })
      else await page.screenshot({ path: file, fullPage: !!extra.full })
      const step = { id, title, url: page.url().replace(BASE, '').replace(process.env.FLOWMAP_WS || '\u0000', '…'), file, ...('desc' in extra ? { desc: extra.desc } : {}) }
      const i = steps.findIndex(x => x.id === id); if (i >= 0) steps[i] = step; else steps.push(step)
      fs.writeFileSync(`${out}/steps.json`, JSON.stringify(steps, null, 2))
      console.log(`shot ${id} ${step.url}`)
      return step
    },
    async dump(label = '') {
      const items = await page.locator('button, a, [role=button], [role=menuitem], [role=tab], [role=option], input, textarea, select').evaluateAll(els => els
        .filter(e => e.offsetParent !== null || e.getClientRects().length)
        .map(e => `${e.tagName.toLowerCase()}${e.getAttribute('role') ? '[' + e.getAttribute('role') + ']' : ''} ${(e.getAttribute('aria-label') || e.getAttribute('placeholder') || e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60)}`))
      console.log(`--- controls ${label} (${page.url().replace(BASE, '')}):\n` + [...new Set(items)].filter(x => !(process.env.FLOWMAP_DUMP_HIDE && new RegExp(process.env.FLOWMAP_DUMP_HIDE).test(x))).slice(0, 120).join('\n'))
    },
    async close() { await browser.close() },
  }
  async function settle(ms = 700) {
    await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {})
    await page.waitForTimeout(ms)
  }
  s.settle = settle
  return s
}

export async function run(journey, persona, body, opts) {
  const s = await session(journey, persona, opts)
  try {
    if (!fs.existsSync(`${DIR}/auth/${persona}.json`) || opts?.relogin) await s.login(persona)
    await body(s)
  } catch (e) {
    console.log('FAILED:', String(e.message).split('\n')[0])
    await s.page.screenshot({ path: `${s.out}/zz-failure.png` }).catch(() => {})
    await s.dump('failure').catch(() => {})
    process.exitCode = 1
  } finally {
    await s.close()
  }
}

// Click the first menu-like item (checkbox, radio, item, option) whose accessible name matches.
export async function clickItem(page, re) {
  for (const role of ['menuitemcheckbox', 'menuitemradio', 'menuitem', 'option', 'button']) {
    const l = page.getByRole(role, { name: re })
    if (await l.count()) { await l.first().click(); return true }
  }
  const t = page.getByText(re)
  if (await t.count()) { await t.first().click(); return true }
  throw new Error(`no item matching ${re}`)
}

// Click the first result row rendered right under a search input inside a popover.
export async function clickFirstResult(page, input, offset = 40) {
  const b = await input.boundingBox()
  await page.mouse.click(b.x + 70, b.y + b.height + offset)
}

// Open a project's overview from the Boards view, whether its sidebar row starts expanded or collapsed.
export async function openProject(s, name) {
  const p = s.page
  await s.go('?view=boards'); await p.waitForTimeout(2500)
  const overview = p.getByRole('button', { name: `Overview for ${name}` })
  if (!(await overview.isVisible().catch(() => false))) {
    const row = p.getByRole('button', { name, exact: true })
    if (await row.count()) await row.first().click()
    await p.waitForTimeout(1200)
  }
  if (await overview.isVisible().catch(() => false)) await overview.click()
  await p.waitForTimeout(2000)
}

// Run one capture step; on failure, log it and keep going so one broken selector does not cost the whole journey.
export async function step(s, label, fn) {
  try { await fn(); return true } catch (e) {
    console.log(`STEP FAILED ${label}: ${String(e.message).split('\n')[0].slice(0, 160)}`)
    await s.page.screenshot({ path: `${s.out}/zz-${label}.png` }).catch(() => {})
    return false
  }
}
