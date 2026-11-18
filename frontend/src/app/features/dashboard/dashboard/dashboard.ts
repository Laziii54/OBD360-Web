import { Component, computed, effect, inject, untracked } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DtcScanService } from '../../../core/services/dtc-scan.service';
import { LiveDataService } from '../../../core/services/live-data.service';
import { LIVE_PIDS, convertReading } from '../../../core/services/obd-decoder';
import { ObdBluetooth } from '../../../core/services/obd-bluetooth.service';
import { UserSettings } from '../../../core/services/user-settings.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [DatePipe, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  private readonly live = inject(LiveDataService);
  private readonly settings = inject(UserSettings);

  readonly adapter = inject(ObdBluetooth);
  readonly scanner = inject(DtcScanService);

  readonly activeCodes = computed(() => {
    const results = this.scanner.results();
    return new Set([...results['03'], ...results['0A']].map((finding) => finding.code)).size;
  });

  constructor() {
    effect((onCleanup) => {
      if (this.adapter.isConnected()) {
        untracked(() => this.live.start());
      }
      onCleanup(() => this.live.stop());
    });
  }

  metric(id: string): string {
    const pid = LIVE_PIDS.find((item) => item.id === id);
    const value = this.live.readings()[id]?.value;
    if (!pid || value === undefined) {
      return '--';
    }
    return convertReading(value, pid.unit, this.settings.unitSystem()).value.toFixed(pid.digits);
  }

  unit(id: string): string {
    const pid = LIVE_PIDS.find((item) => item.id === id);
    return pid ? convertReading(0, pid.unit, this.settings.unitSystem()).unit : '';
  }
}
