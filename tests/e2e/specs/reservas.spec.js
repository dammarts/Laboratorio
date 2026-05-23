const { test, expect } = require('@playwright/test');
const { loginEnUI } = require('../fixtures/auth.fixture');

const DOCENTE_EMAIL = process.env.E2E_DOCENTE_EMAIL || 'jp@universidad.edu';
const DOCENTE_PASSWORD = process.env.E2E_DOCENTE_PASSWORD || 'test1234';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

test.describe('Gestión de reservas (Docente)', () => {

  test.beforeEach(async ({ page }) => {
    await loginEnUI(page, DOCENTE_EMAIL, DOCENTE_PASSWORD);
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });
  });

  test('docente ve el formulario de nueva reserva', async ({ page }) => {
    await page.goto('/reservas/nueva');

    await expect(page.getByRole('heading', { name: 'Nueva reserva' })).toBeVisible({ timeout: 5_000 });
    await expect(page.locator('select').first()).toBeVisible();
    await expect(page.locator('input[type="date"]')).toBeVisible();
    await expect(page.getByPlaceholder(/Redes/i)).toBeVisible();
  });

  test('docente crea una reserva exitosamente', async ({ page }) => {
    await page.goto('/reservas/nueva');

    // Seleccionar primer laboratorio
    const labSelect = page.locator('select').first();
    await labSelect.selectOption({ index: 1 });

    // Fecha de mañana
    const hoy = new Date();
    hoy.setDate(hoy.getDate() + 1);
    const fecha = hoy.toISOString().split('T')[0];
    await page.locator('input[type="date"]').fill(fecha);

    await page.getByPlaceholder(/Redes/i).fill('Prueba E2E automatizada');

    // Los botones de slot muestran la hora (ej. "08:00") — esperar hasta 8s
    const primerSlot = page.locator('button').filter({ hasText: /\d{2}:\d{2}/ }).first();
    await primerSlot.waitFor({ state: 'visible', timeout: 8_000 });
    await primerSlot.click();

    await page.getByRole('button', { name: /confirmar reserva/i }).click();

    await expect(
      page.getByText(/reserva creada/i)
    ).toBeVisible({ timeout: 10_000 });
  });

  test('docente cancela una reserva existente', async ({ page, request }) => {
    // Crear reserva ACTIVA via API antes de cada intento (para que retries funcionen)
    const loginResp = await request.post(`${BACKEND_URL}/auth/login`, {
      data: { email: DOCENTE_EMAIL, password: DOCENTE_PASSWORD },
    });
    const { access_token } = await loginResp.json();
    await request.post(`${BACKEND_URL}/reservas/`, {
      headers: { Authorization: `Bearer ${access_token}` },
      data: {
        laboratorio_id: 1,
        curso: 'Reserva E2E para cancelar',
        fecha: '2026-06-30',
        hora_inicio: '08:00:00',
        hora_fin: '10:00:00',
      },
    });

    await page.goto('/historial');

    const btnCancelar = page.getByRole('button', { name: /^cancelar$/i }).first();
    await expect(btnCancelar).toBeVisible({ timeout: 8_000 });
    await btnCancelar.click();

    await page.getByPlaceholder(/motivo/i).fill('Cancelación por prueba e2e');
    await page.getByRole('button', { name: /confirmar cancelaci[oó]n/i }).click();

    // El badge usa <span> con texto exacto "Cancelada"
    await expect(
      page.locator('span').filter({ hasText: 'Cancelada' }).first()
    ).toBeVisible({ timeout: 8_000 });
  });

});
