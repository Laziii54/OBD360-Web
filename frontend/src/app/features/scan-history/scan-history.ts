import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ScanHistoryApi, ScanRecord } from '../../core/services/scan-history.service';

@Component({
  imports: [DatePipe],
  selector: 'app-scan-history',
  styleUrl: './scan-history.scss',
  templateUrl: './scan-history.html',
})
export class ScanHistory {
  private readonly api = inject(ScanHistoryApi);

  readonly loading = signal(true);
  readonly failed = signal(false);
  readonly scans = signal<ScanRecord[]>([]);
  readonly search = signal('');

  readonly filtered = computed(() => {
    const term = this.search().trim().toLowerCase();
    return this.scans().filter(
      (scan) =>
        !term ||
        scan.vehicle.toLowerCase().includes(term) ||
        scan.vin?.toLowerCase().includes(term) ||
        scan.codes.some((code) => code.toLowerCase().includes(term))
    );
  });

  readonly completed = computed(() => this.scans().filter((scan) => scan.endedAt).length);
  readonly faults = computed(() => this.scans().reduce((sum, scan) => sum + scan.codes.length, 0));
  readonly vehicles = computed(() => new Set(this.scans().map((scan) => scan.vin ?? scan.vehicle)).size);
  readonly latest = computed(() => this.scans()[0] ?? null);

  constructor() {
    this.api.list().subscribe({
      next: (scans) => {
        this.scans.set(scans);
        this.loading.set(false);
      },
      error: () => {
        this.failed.set(true);
        this.loading.set(false);
      },
    });
  }

  duration(scan: ScanRecord): string {
    if (!scan.endedAt) {
      return '--';
    }
    const seconds = Math.max(0, (Date.parse(scan.endedAt) - Date.parse(scan.startedAt)) / 1000);
    return `${Math.round(seconds)} s`;
  }
}
