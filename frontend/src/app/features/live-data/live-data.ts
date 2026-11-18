import { Component, computed, effect, inject, signal, untracked } from '@angular/core';
import { LIVE_PIDS, PidDefinition, convertReading } from '../../core/services/obd-decoder';
import { LiveDataService } from '../../core/services/live-data.service';
import { ObdBluetooth } from '../../core/services/obd-bluetooth.service';
import { UserSettings } from '../../core/services/user-settings.service';

@Component({
  imports: [],
  selector: 'app-live-data',
  styleUrl: './live-data.scss',
  templateUrl: './live-data.html',
})
export class LiveData {
  private readonly settings = inject(UserSettings);

  readonly adapter = inject(ObdBluetooth);
  readonly live = inject(LiveDataService);

  readonly pids = LIVE_PIDS;
  readonly refreshRates = [250, 500, 1000, 2000];
  readonly chartPid = signal(LIVE_PIDS[0].id);

  readonly statusLabel = computed(() => {
    if (!this.adapter.isConnected()) {
      return 'WAITING FOR CONNECTION';
    }
    return this.live.paused() ? 'PAUSED' : 'STREAMING';
  });

  readonly chartValues = computed(() => this.live.readings()[this.chartPid()]?.history ?? []);

  readonly chartPoints = computed(() => {
    const values = this.chartValues();
    if (values.length < 2) {
      return '';
    }

    const min = Math.min(...values);
    const range = Math.max(...values) - min || 1;
    return values
      .map((value, index) => `${(index / (values.length - 1)) * 100},${100 - ((value - min) / range) * 100}`)
      .join(' ');
  });

  constructor() {
    effect((onCleanup) => {
      if (this.adapter.isConnected()) {
        untracked(() => this.live.start());
      }
      onCleanup(() => this.live.stop());
    });
  }

  display(pid: PidDefinition): string {
    const value = this.live.readings()[pid.id]?.value;
    if (value === undefined) {
      return '--';
    }
    return convertReading(value, pid.unit, this.settings.unitSystem()).value.toFixed(pid.digits);
  }

  unit(pid: PidDefinition): string {
    return convertReading(0, pid.unit, this.settings.unitSystem()).unit;
  }

  state(pid: PidDefinition): string {
    if (this.live.unsupported().has(pid.id)) {
      return 'Not supported';
    }
    return this.live.readings()[pid.id] ? 'Live' : 'Waiting';
  }

  togglePause(): void {
    this.live.paused.update((paused) => !paused);
  }
}
