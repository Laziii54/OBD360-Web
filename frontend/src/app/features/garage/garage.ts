import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Vehicle, VehicleInput, VehiclesApi } from '../../core/services/vehicles.service';

@Component({
  imports: [DatePipe, ReactiveFormsModule],
  selector: 'app-garage',
  styleUrl: './garage.scss',
  templateUrl: './garage.html',
})
export class Garage {
  private readonly api = inject(VehiclesApi);
  private readonly fb = inject(FormBuilder);

  readonly loading = signal(true);
  readonly failed = signal(false);
  readonly vehicles = signal<Vehicle[]>([]);
  readonly search = signal('');

  readonly showForm = signal(false);
  readonly editing = signal<Vehicle | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    make: ['', [Validators.required, Validators.maxLength(60)]],
    model: ['', [Validators.required, Validators.maxLength(60)]],
    year: [
      new Date().getFullYear(),
      [Validators.required, Validators.min(1900), Validators.max(2100)],
    ],
    vin: ['', [Validators.pattern(/^$|^[A-HJ-NPR-Z0-9]{17}$/i)]],
    plateNumber: ['', [Validators.maxLength(20)]],
  });

  readonly filtered = computed(() => {
    const term = this.search().trim().toLowerCase();

    return this.vehicles().filter(
      (vehicle) =>
        !term ||
        `${vehicle.make} ${vehicle.model}`.toLowerCase().includes(term) ||
        vehicle.vin?.toLowerCase().includes(term) ||
        vehicle.plateNumber?.toLowerCase().includes(term)
    );
  });

  readonly totalScans = computed(() =>
    this.vehicles().reduce((sum, vehicle) => sum + vehicle.scanCount, 0)
  );

  readonly latestScan = computed(() => {
    const dates = this.vehicles()
      .map((vehicle) => vehicle.lastScanAt)
      .filter((date): date is string => Boolean(date));

    return dates.length ? dates.sort().at(-1)! : null;
  });

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.failed.set(false);

    this.api.list().subscribe({
      next: (vehicles) => {
        this.vehicles.set(vehicles);
        this.loading.set(false);
      },
      error: () => {
        this.failed.set(true);
        this.loading.set(false);
      },
    });
  }

  startCreate(): void {
    this.editing.set(null);
    this.formError.set(null);
    this.form.reset({
      make: '',
      model: '',
      year: new Date().getFullYear(),
      vin: '',
      plateNumber: '',
    });
    this.showForm.set(true);
  }

  startEdit(vehicle: Vehicle): void {
    this.editing.set(vehicle);
    this.formError.set(null);
    this.form.setValue({
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year,
      vin: vehicle.vin ?? '',
      plateNumber: vehicle.plateNumber ?? '',
    });
    this.showForm.set(true);
  }

  cancel(): void {
    this.showForm.set(false);
    this.editing.set(null);
    this.formError.set(null);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    const input: VehicleInput = {
      make: raw.make.trim(),
      model: raw.model.trim(),
      year: Number(raw.year),
      vin: raw.vin.trim() ? raw.vin.trim().toUpperCase() : null,
      plateNumber: raw.plateNumber.trim() ? raw.plateNumber.trim() : null,
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
      this.formError.set(error.error?.message ?? 'მანქანის შენახვა ვერ მოხდა. სცადე ხელახლა.');
    };

    const editing = this.editing();
    if (editing) {
      this.api.update(editing.id, input).subscribe({ next: onSuccess, error: onError });
    } else {
      this.api.create(input).subscribe({ next: onSuccess, error: onError });
    }
  }

  remove(vehicle: Vehicle): void {
    const confirmed = confirm(
      `წავშალო ${vehicle.make} ${vehicle.model}? მასთან ერთად წაიშლება ყველა სკანირება.`
    );

    if (!confirmed) {
      return;
    }

    this.api.delete(vehicle.id).subscribe({
      next: () => this.load(),
      error: () => this.failed.set(true),
    });
  }
}
