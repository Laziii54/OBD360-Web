import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Auth } from '../../../core/services/auth';
import { ForgotPasswordResponse } from '../../../core/models/auth.model';

@Component({
  imports: [ReactiveFormsModule, RouterLink],
  selector: 'app-forgot-password',
  styleUrl: './forgot-password.scss',
  templateUrl: './forgot-password.html',
})
export class ForgotPassword {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(Auth);

  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly result = signal<ForgotPasswordResponse | null>(null);

  readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.auth.forgotPassword(this.form.getRawValue()).subscribe({
      next: (response) => {
        this.result.set(response);
        this.isSubmitting.set(false);
      },
      error: (error: HttpErrorResponse) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(
          error.error?.message ?? 'მოთხოვნა ვერ გაიგზავნა. სცადე ხელახლა.'
        );
      },
    });
  }
}
