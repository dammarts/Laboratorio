const { test, expect } = require('@playwright/test');

const RUTAS_PROTEGIDAS = [
  '/laboratorios',
  '/reservas',
  '/historial',
  '/reportes',
];

test.describe('Control de acceso', () => {

  for (const ruta of RUTAS_PROTEGIDAS) {
    test(`sin token, ${ruta} redirige a /login`, async ({ page }) => {
      await page.context().clearCookies();
      await page.evaluate(() => localStorage.clear());

      await page.goto(ruta);

      await expect(page).toHaveURL(/\/login/, { timeout: 8_000 });
    });
  }

  test('navegar a /login con sesión activa redirige fuera del login', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/correo|email/i).fill(
      process.env.E2E_ADMIN_EMAIL || 'admin@uni.edu'
    );
    await page.getByLabel(/contraseña|password/i).fill(
      process.env.E2E_ADMIN_PASSWORD || 'Admin123!'
    );
    await page.getByRole('button', { name: /ingresar|login|entrar/i }).click();
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });

    await page.goto('/login');
    await expect(page).not.toHaveURL(/\/login/, { timeout: 5_000 });
  });

});
