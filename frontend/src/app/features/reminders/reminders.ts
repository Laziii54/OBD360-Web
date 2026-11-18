import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Reminder, ReminderInput, RemindersApi } from '../../core/services/reminders.service';
import { Vehicle, VehiclesApi } from '../../core/services/vehicles.service';

type ReminderFilter = 'all' | 'pending' | 'overdue' | 'done';

@Component({
  imports: [DatePipe, DecimalPipe, ReactiveFormsModule, RouterLink],
  selector: 'app-reminders',
  styleUrl: './reminders.scss',
  templateUrl: './reminders.html',
})
export class Reminders {
  private readonly api = inject(RemindersApi);
  private readonly vehiclesApi = inject(VehiclesApi);
  private readonly fb = inject(FormBuilder);

  readonly loading = signal(true);
  readonly failed = signal(false);
  readonly reminders = signal<Reminder[]>([]);
  readonly vehicles = signal<Vehicle[]>([]);
  readonly filter = signal<ReminderFilter>('all');

  readonly showForm = signal(false);
  readonly editing = signal<Reminder | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    vehicleId: ['', [Validators.required]],
    type: ['', [Validators.required, Validators.maxLength(80)]],
    dueAtKm: [0, [Validators.min(0), Validators.max(2_000_000)]],
    dueAtDate: [''],
  });

  readonly pending = computed(
    () => this.reminders().filter((reminder) => reminder.status === 'pending').length
  );

  readonly overdue = computed(
    () => this.reminders().filter((reminder) => reminder.status === 'overdue').length
  );

  readonly done = computed(
    () => this.reminders().filter((reminder) => reminder.status === 'done').length
  );

  readonly filtered = computed(() => {
    const filter = this.filter();
    return filter === 'all'
      ? this.reminders()
      : this.reminders().filter((reminder) => reminder.status === filter);
  });

  constructor() {
    this.vehiclesApi.list().subscribe({
      next: (vehicles) => this.vehicles.set(vehicles),
      error: () => this.vehicles.set([]),
    });
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.failed.set(false);

    this.api.list().subscribe({
      next: (reminders) => {
        this.reminders.set(reminders);
        this.loading.set(false);
      },
      error: () => {
        this.failed.set(true);
        this.loading.set(false);
      },
    });
  }

  setFilter(filter: ReminderFilter): void {
    this.filter.set(filter);
  }

  startCreate(): void {
    this.editing.set(null);
    this.formError.set(null);
    this.form.controls.vehicleId.enable();
    this.form.reset({
      vehicleId: this.vehicles()[0]?.id ?? '',
      type: '',
      dueAtKm: 0,
      dueAtDate: '',
    });
    this.showForm.set(true);
  }

  startEdit(reminder: Reminder): void {
    this.editing.set(reminder);
    this.formError.set(null);
    this.form.setValue({
      vehicleId: reminder.vehicleId,
      type: reminder.type,
      dueAtKm: reminder.dueAtKm ?? 0,
      dueAtDate: reminder.dueAtDate ?? '',
    });
    this.form.controls.vehicleId.disable();
    this.showForm.set(true);
  }

  cancel(): void {
    this.showForm.set(false);
    this.editing.set(null);
    this.form.controls.vehicleId.enable();
    this.formError.set(null);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    const input: ReminderInput = {
      vehicleId: raw.vehicleId,
      type: raw.type.trim(),
      dueAtKm: Number(raw.dueAtKm) > 0 ? Number(raw.dueAtKm) : null,
      dueAtDate: raw.dueAtDate || null,
    };

    this.saving.set(true);
    this.formError.set(null);

    const onSuccess = () => {
      this.saving.set(false);
      this.showForm.set(false);
      this.editing.set(null);
      this.load();
    };

    const onError = (error: HttpErrorResponse) => {
      this.saving.set(false);
      this.formError.set(error.error?.message ?? 'შეხსენების შენახვა ვერ მოხდა.');
    };

    const editing = this.editing();
    if (editing) {
      this.api.update(editing.id, input).subscribe({ next: onSuccess, error: onError });
    } else {
      this.api.create(input).subscribe({ next: onSuccess, error: onError });
    }
  }

  complete(reminder: Reminder): void {
    this.api.complete(reminder.id).subscribe({ next: () => this.load() });
  }

  remove(reminder: Reminder): void {
    if (!confirm(`წავშალო შეხსენება „${reminder.type}“?`)) {
      return;
    }

    this.api.delete(reminder.id).subscribe({ next: () => this.load() });
  }
}
