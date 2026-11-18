import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../../../core/services/auth';

@Component({
  imports: [ReactiveFormsModule, RouterLink],
  selector: 'app-register',
  styleUrl: './register.scss',
  templateUrl: './register.html',
})
export class Register {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);

  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    displayName: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    password: [
      '',
      [
        Validators.required,
        Validators.minLength(8),
        Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$/),
      ],
    ],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.auth.register(this.form.getRawValue()).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.router.navigateByUrl('/dashboard');
      },
      error: (err) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(this.extractErrorMessage(err));
      },
    });
  }

  private extractErrorMessage(err: { status?: number; error?: { errors?: Record<string, string[]> } }): string {
    if (err?.status === 0) {
      return 'სერვერთან კავშირი ვერ დამყარდა. შეამოწმე, გაშვებულია თუ არა ბექენდი.';
    }

    if (err?.status === 409) {
      return 'ეს ელფოსტა უკვე დარეგისტრირებულია.';
    }

    const validationErrors = err?.error?.errors;
    if (validationErrors) {
      const messages = Object.values(validationErrors).flat();
      if (messages.length > 0) {
        return messages.join(' ');
      }
    }

    if (err?.status && err.status >= 500) {
      return 'სერვერის შეცდომა. სცადე მოგვიანებით.';
    }

    return 'რეგისტრაცია ვერ შედგა. გადაამოწმე მონაცემები.';
  }
}
