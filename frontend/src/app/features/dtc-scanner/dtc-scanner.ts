import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { DtcScanService } from '../../core/services/dtc-scan.service';
import { DtcMode } from '../../core/services/obd-decoder';
import { ObdBluetooth } from '../../core/services/obd-bluetooth.service';
import { UserSettings } from '../../core/services/user-settings.service';

const MONITOR_LABELS = { ready: 'Ready', incomplete: 'Incomplete', unsupported: 'N/A' } as const;

@Component({
  imports: [DatePipe],
  selector: 'app-dtc-scanner',
  styleUrl: './dtc-scanner.scss',
  templateUrl: './dtc-scanner.html',
})
export class DtcScanner {
  private readonly settings = inject(UserSettings);

  readonly adapter = inject(ObdBluetooth);
  readonly scanner = inject(DtcScanService);

  readonly tabs: { mode: DtcMode; label: string }[] = [
    { mode: '03', label: 'Stored' },
    { mode: '07', label: 'Pending' },
    { mode: '0A', label: 'Permanent' },
  ];
  readonly monitorLabels = MONITOR_LABELS;

  readonly activeMode = signal<DtcMode>('03');
  readonly confirmingClear = signal(false);

  readonly findings = computed(() => this.scanner.results()[this.activeMode()]);
  readonly canScan = computed(
    () => this.adapter.isConnected() && !this.scanner.scanning() && !this.scanner.clearing()
  );

  count(mode: DtcMode): number | string {
    return this.scanner.hasScanned() ? this.scanner.results()[mode].length : '--';
  }

  requestClear(): void {
    if (this.settings.confirmClear()) {
      this.confirmingClear.set(true);
    } else {
      this.clearCodes();
    }
  }

  clearCodes(): void {
    this.confirmingClear.set(false);
    void this.scanner.clearCodes();
  }
}
