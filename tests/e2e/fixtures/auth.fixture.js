const { request } = require('@playwright/test');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

async function obtenerToken(email, password) {
  const ctx = await request.newContext();
  const res = await ctx.post(`${BACKEND_URL}/auth/login`, {
    data: { email, password },
  });
  if (!res.ok()) {
    throw new Error(`Login fallido para ${email}: ${res.status()}`);
  }
  const body = await res.json();
  await ctx.dispose();
  return body.access_token;
}

async function loginEnUI(page, email, password) {
  await page.goto('/login');
  await page.locator('input[type="email"]').fill(email);
  await page.locator('input[type="password"]').fill(password);
  await page.getByRole('button', { name: /iniciar.*sesi[oó]n|ingresar|login|entrar/i }).click();
}

module.exports = { obtenerToken, loginEnUI };
