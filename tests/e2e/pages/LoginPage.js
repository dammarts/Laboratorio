class LoginPage {
  constructor(page) {
    this.page = page;
    this.inputEmail = page.getByLabel(/correo|email/i);
    this.inputPassword = page.getByLabel(/contraseña|password/i);
    this.btnSubmit = page.getByRole('button', { name: /ingresar|login|entrar/i });
    this.mensajeError = page.getByRole('alert');
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
