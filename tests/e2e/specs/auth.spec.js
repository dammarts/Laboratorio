const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@laboratorio.com';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'Admin123!';

test.describe('Autenticación', () => {

  test('login exitoso redirige al dashboard', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(ADMIN_EMAIL, ADMIN_PASSWORD);

    await expect(page).not.toHaveURL(/\/login/, { timeout: 8_000 });
    await expect(page).toHaveURL(/\/(dashboard|home|laboratorios|reservas)?/, { timeout: 8_000 });
  });

  test('login con credenciales incorrectas muestra error', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('noexiste@uni.edu', 'clavemal123');

    const errorText = await loginPage.esperarError();
    expect(errorText).toBeTruthy();
    await expect(page).toHaveURL(/\/login/);
  });

  test('login con contraseña vacía no envía el formulario', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.inputEmail.fill(ADMIN_EMAIL);
    await loginPage.btnSubmit.click();

    await expect(page).toHaveURL(/\/login/);
  });

});
