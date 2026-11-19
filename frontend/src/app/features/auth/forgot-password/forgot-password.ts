import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Auth } from '../../../core/services/auth';

@Component({
  imports: [ReactiveFormsModule, RouterLink],
  selector: 'app-forgot-password',
  styleUrl: './forgot-password.scss',
  templateUrl: './forgot-password.html',
})
export class ForgotPassword {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(Auth);

  readonly step = signal<'email' | 'reset' | 'done'>('email');
  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly devCode = signal<string | null>(null);
  readonly email = signal('');

  readonly emailForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });

  readonly resetForm = this.fb.nonNullable.group({
    code: ['', [Validators.required, Validators.pattern(/^[0-9]{6}$/)]],
    newPassword: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required]],
  });

  submitEmail(): void {
    if (this.emailForm.invalid) {
      this.emailForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.auth.forgotPassword(this.emailForm.getRawValue()).subscribe({
      next: (response) => {
        this.email.set(this.emailForm.getRawValue().email.trim());
        this.devCode.set(response.devCode);
        this.isSubmitting.set(false);
        this.step.set('reset');
      },
      error: (error: HttpErrorResponse) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(
          error.error?.message ?? 'მოთხოვნა ვერ გაიგზავნა. სცადე ხელახლა.'
        );
      },
    });
  }

  submitReset(): void {
    if (this.resetForm.invalid) {
      this.resetForm.markAllAsTouched();
      return;
    }

    const { code, newPassword, confirmPassword } = this.resetForm.getRawValue();

    if (newPassword !== confirmPassword) {
      this.errorMessage.set('პაროლები არ ემთხვევა.');
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.auth.resetPassword({
      email: this.email(),
      code: code.trim(),
      newPassword,
    }).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.step.set('done');
      },
      error: (error: HttpErrorResponse) => {
        this.isSubmitting.set(false);

        const validationErrors = error.error?.errors as
          | Record<string, string[]>
          | undefined;

        const firstValidationError = validationErrors
          ? Object.values(validationErrors).flat()[0]
          : null;

        this.errorMessage.set(
          firstValidationError ??
            error.error?.message ??
            'კოდი არასწორია ან ვადაგასულია.'
        );
      },
    });
  }

  restart(): void {
    this.step.set('email');
    this.resetForm.reset();
    this.devCode.set(null);
    this.errorMessage.set(null);
  }
}
