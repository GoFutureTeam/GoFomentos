import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

// Função Validadora Customizada
export const passwordsMatchValidator: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
  const password = control.get('password');
  const confirmPassword = control.get('confirmPassword');

  // Retorna null se os campos não estiverem preenchidos ou se as senhas coincidirem
  return password && confirmPassword && password.value === confirmPassword.value ? null : { passwordsDoNotMatch: true };
};

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register-page.component.html',
  styleUrl: './register-page.component.scss'
})
export class RegisterPageComponent {
  registerForm: FormGroup;
  successMessage: string | null = null;
  errorMessage: string | null = null;
  isLoading = false; // Para controlar o spinner

  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  constructor() {
    this.registerForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [
        Validators.required,
        Validators.minLength(8),
        Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).*$/) // Letra minúscula, maiúscula e número
      ]],
      confirmPassword: ['', Validators.required],
    }, { validators: passwordsMatchValidator }); // Adiciona o validador no FormGroup
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched(); // Mostra erros se o formulário for inválido
      return;
    }

    this.isLoading = true;
    this.successMessage = null;
    this.errorMessage = null;

    const { name, email, password } = this.registerForm.value;

    this.authService.register(name, email, password).subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = 'Registro efetuado com sucesso! Você será redirecionado para o login...';
        setTimeout(() => this.router.navigate(['/login']), 3000);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Ocorreu um erro ao tentar registrar. Tente novamente.';
        console.error('Erro no registro (MOCK):', err);
      }
    });
  }

  // Helper para verificar se um campo é inválido e foi tocado
  isInvalid(controlName: string): boolean {
    const control = this.registerForm.get(controlName);
    return !!control && control.invalid && (control.dirty || control.touched);
  }
}
