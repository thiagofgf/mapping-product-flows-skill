// Capture the Tasklet demo journeys: one screenshot per step, straight from the static pages (no server needed).
// Usage: FLOWMAP_PKG=/path/to/a/project/with/playwright/package.json node capture.mjs
import { createRequire } from 'node:module'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(process.env.FLOWMAP_PKG || path.join(process.cwd(), 'package.json'))
const { chromium } = require('playwright')
const APP = pathToFileURL(path.join(here, 'app')).href
const browser = await chromium.launch()
const page = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage()
const shot = async (area, id) => {
  fs.mkdirSync(path.join(here, 'shots', area), { recursive: true })
  await page.waitForTimeout(150)
  await page.screenshot({ path: path.join(here, 'shots', area, id + '.png') })
  console.log('shot', area, id)
}
const go = p => page.goto(`${APP}/${p}`)
// 01-access
await go('signup.html'); await shot('access', '01-signup')
await page.fill('#email', 'ana@northwind.example'); await page.fill('#pw', 'short'); await page.click('button[type=submit]'); await shot('access', '02-signup-short-password')
await page.fill('#pw', 'correct horse'); await page.click('button[type=submit]'); await page.waitForURL(/check-email/); await shot('access', '03-check-email')
await go('email-confirm.html'); await shot('access', '04-email-confirm')
await go('login.html'); await shot('access', '05-login')
await page.fill('#pw', 'wrong'); await page.click('button[type=submit]'); await shot('access', '06-login-wrong')
await page.click('text=Forgot password?'); await shot('access', '07-forgot-404')
await go('signup.html'); await page.click('text=Continue with Lumen ID'); await shot('access', '08-provider')
await page.click('.acct'); await shot('access', '09-signed-in')
// 02-tasks
await go('tasks.html'); await shot('tasks', '01-tasks')
await page.click('#add'); await shot('tasks', '02-new-task')
await page.click('#save'); await page.waitForURL(/created=/); await shot('tasks', '03-task-created')
await go('email-assigned.html'); await shot('tasks', '04-email-assigned')
await go('tasks.html?f=week'); await shot('tasks', '05-filter-week')
await go('tasks.html?f=late'); await shot('tasks', '06-filter-late')
await go('tasks.html?f=none'); await shot('tasks', '07-filter-empty')
await browser.close()
