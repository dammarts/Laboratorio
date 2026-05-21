const { test, expect } = require('@playwright/test');
const { loginEnUI } = require('../fixtures/auth.fixture');

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@uni.edu';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'Admin123!';

test.describe('Panel de reportes (Admin)', () => {

  test.beforeEach(async ({ page }) => {
    await loginEnUI(page, ADMIN_EMAIL, ADMIN_PASSWORD);
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });
  });

  test('admin ve el panel de reportes con datos', async ({ page }) => {
    await page.goto('/reportes');

    await expect(page).toHaveURL(/\/reportes/, { timeout: 5_000 });
    await expect(
      page.getByRole('heading', { name: /reporte|reportes/i })
    ).toBeVisible({ timeout: 5_000 });

    await expect(
      page.getByRole('tab', { name: /uso.*laboratorio|laboratorio/i })
    ).toBeVisible();
  });

  test('admin puede cambiar de tab en reportes', async ({ page }) => {
    await page.goto('/reportes');

    await page.getByRole('tab', { name: /ocupaci[oó]n.*mensual|mensual/i }).click();
    await expect(
      page.getByRole('tab', { name: /ocupaci[oó]n.*mensual|mensual/i })
    ).toHaveAttribute('aria-selected', 'true');

    await page.getByRole('tab', { name: /docente/i }).click();
    await expect(
      page.getByRole('tab', { name: /docente/i })
    ).toHaveAttribute('aria-selected', 'true');
  });

  test('admin puede descargar CSV de uso por laboratorio', async ({ page }) => {
    await page.goto('/reportes');

    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 10_000 }),
      page.getByRole('button', { name: /exportar.*csv|descargar.*csv/i }).first().click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/\.csv$/i);
  });

  test('docente sin rol admin no puede acceder a /reportes', async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

    await loginEnUI(
      page,
      process.env.E2E_DOCENTE_EMAIL || 'docente@uni.edu',
      process.env.E2E_DOCENTE_PASSWORD || 'Docente123!'
    );
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });

    await page.goto('/reportes');

    await expect(page).not.toHaveURL(/\/reportes/, { timeout: 5_000 });
  });

});
