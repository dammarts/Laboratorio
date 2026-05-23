const { test, expect } = require('@playwright/test');
const { loginEnUI } = require('../fixtures/auth.fixture');

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@laboratorio.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'Admin123!';

const RUTAS_PROTEGIDAS = [
  '/laboratorios',
  '/reservas/nueva',
  '/historial',
  '/reportes',
];

test.describe('Control de acceso', () => {

  for (const ruta of RUTAS_PROTEGIDAS) {
    test(`sin token, ${ruta} redirige a /login`, async ({ page }) => {
      // addInitScript corre antes de cualquier JS de la página, borrando el token
      // antes de que React lo lea — evita la race condition con page.evaluate
      await page.addInitScript(() => {
        localStorage.clear();
        sessionStorage.clear();
      });

      await page.goto(ruta);

      await expect(page).toHaveURL(/\/login/, { timeout: 8_000 });
    });
  }

  test('login exitoso redirige fuera de /login', async ({ page }) => {
    await loginEnUI(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });
  });

  test('rol DOCENTE no puede acceder a /reportes', async ({ page }) => {
    await loginEnUI(
      page,
      process.env.E2E_DOCENTE_EMAIL || 'jp@universidad.edu',
      process.env.E2E_DOCENTE_PASSWORD || 'test1234'
    );
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });

    await page.goto('/reportes');
    await expect(page).not.toHaveURL(/\/reportes/, { timeout: 5_000 });
  });

});
