const { test, expect } = require('@playwright/test');
const { loginEnUI } = require('../fixtures/auth.fixture');

const DOCENTE_EMAIL = process.env.E2E_DOCENTE_EMAIL || 'docente@uni.edu';
const DOCENTE_PASSWORD = process.env.E2E_DOCENTE_PASSWORD || 'Docente123!';

test.describe('Gestión de reservas (Docente)', () => {

  test.beforeEach(async ({ page }) => {
    await loginEnUI(page, DOCENTE_EMAIL, DOCENTE_PASSWORD);
    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });
  });

  test('docente crea una reserva exitosamente', async ({ page }) => {
    await page.goto('/reservas');

    await page.getByRole('button', { name: /nueva reserva|crear reserva/i }).click();

    await page.getByLabel(/laboratorio/i).selectOption({ index: 1 });

    const hoy = new Date();
    hoy.setDate(hoy.getDate() + 1);
    const fecha = hoy.toISOString().split('T')[0];
    await page.getByLabel(/fecha/i).fill(fecha);
    await page.getByLabel(/hora.*inicio/i).fill('09:00');
    await page.getByLabel(/hora.*fin/i).fill('11:00');

    await page.getByRole('button', { name: /confirmar|guardar|reservar/i }).click();

    await expect(
      page.getByRole('alert').or(page.getByText(/reserva.*creada|exitosa/i))
    ).toBeVisible({ timeout: 8_000 });
  });

  test('docente cancela una reserva existente', async ({ page }) => {
    await page.goto('/historial');

    const primeraReserva = page.getByRole('row').nth(1);
    await expect(primeraReserva).toBeVisible({ timeout: 5_000 });

    await primeraReserva.getByRole('button', { name: /cancelar/i }).click();

    await page.getByLabel(/motivo/i).fill('Cancelación por prueba e2e');
    await page.getByRole('button', { name: /confirmar|aceptar/i }).click();

    await expect(
      page.getByRole('alert').or(page.getByText(/cancelada|cancelación.*exitosa/i))
    ).toBeVisible({ timeout: 8_000 });
  });

});
