const { test, expect } = require('@playwright/test');
const { loginEnUI } = require('../fixtures/auth.fixture');

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@laboratorio.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'Admin123!';

test.describe('Panel de reportes (Admin)', () => {

  test.beforeEach(async ({ page }) => {
    await loginEnUI(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });
  });

  test('admin ve el panel de reportes', async ({ page }) => {
    await page.goto('/reportes');

    await expect(page).toHaveURL(/\/reportes/, { timeout: 5_000 });
    await expect(page.getByRole('heading', { name: /reportes/i })).toBeVisible({ timeout: 5_000 });

    // Las pestañas son botones simples
    await expect(page.getByRole('button', { name: /uso.*laboratorio/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /ocupaci[oó]n.*mensual/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /por docente/i })).toBeVisible();
  });

  test('admin puede cambiar de pestaña en reportes', async ({ page }) => {
    await page.goto('/reportes');

    await page.getByRole('button', { name: /ocupaci[oó]n.*mensual/i }).click();
    await expect(page.locator('select').first()).toBeVisible({ timeout: 5_000 });

    await page.getByRole('button', { name: /por docente/i }).click();
    await expect(page.getByRole('button', { name: /csv/i })).toBeVisible({ timeout: 5_000 });
  });

  test('admin puede descargar CSV de uso por laboratorio', async ({ page }) => {
    await page.goto('/reportes');

    // La pestaña "Uso por laboratorio" está activa por defecto
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 10_000 }),
      page.getByRole('button', { name: /csv/i }).first().click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/\.csv$/i);
  });

  test('docente no puede acceder a /reportes', async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

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
