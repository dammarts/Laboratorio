class LoginPage {
  constructor(page) {
    this.page = page;
    this.inputEmail = page.locator('input[type="email"]');
    this.inputPassword = page.locator('input[type="password"]');
    this.btnSubmit = page.getByRole('button', { name: /iniciar.*sesi[oó]n|ingresar|login|entrar/i });
    this.mensajeError = page.getByTestId('login-error');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email, password) {
    await this.inputEmail.fill(email);
    await this.inputPassword.fill(password);
    await this.btnSubmit.click();
  }

  async esperarError() {
    await this.mensajeError.waitFor({ state: 'visible', timeout: 5_000 });
    return this.mensajeError.textContent();
  }
}

module.exports = { LoginPage };
