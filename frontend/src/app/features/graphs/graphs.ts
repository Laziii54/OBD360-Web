import { Component, computed, effect, inject, untracked } from '@angular/core';
import { LiveDataService } from '../../core/services/live-data.service';
import { LIVE_PIDS, PidDefinition, convertReading } from '../../core/services/obd-decoder';
import { ObdBluetooth } from '../../core/services/obd-bluetooth.service';
import { UserSettings } from '../../core/services/user-settings.service';

const GRAPH_IDS = ['rpm', 'speed', 'coolant', 'load', 'throttle'];

@Component({
  imports: [],
  selector: 'app-graphs',
  styleUrl: './graphs.scss',
  templateUrl: './graphs.html',
})
export class Graphs {
  private readonly settings = inject(UserSettings);

  readonly adapter = inject(ObdBluetooth);
  readonly live = inject(LiveDataService);

  readonly graphs = computed(() =>
    LIVE_PIDS.filter((pid) => GRAPH_IDS.includes(pid.id)).map((pid) => this.toGraph(pid))
  );

  constructor() {
    effect((onCleanup) => {
      if (this.adapter.isConnected()) {
        untracked(() => this.live.start());
      }
      onCleanup(() => this.live.stop());
    });
  }

  private toGraph(pid: PidDefinition) {
    const values = this.live.readings()[pid.id]?.history ?? [];
    const latest = values.at(-1);
    const shown = latest === undefined ? null : convertReading(latest, pid.unit, this.settings.unitSystem());
    const min = Math.min(...values);
    const range = Math.max(...values) - min || 1;

    return {
      id: pid.id,
      name: pid.name,
      unit: convertReading(0, pid.unit, this.settings.unitSystem()).unit,
      value: shown ? shown.value.toFixed(pid.digits) : '--',
      unsupported: this.live.unsupported().has(pid.id),
      points:
        values.length < 2
          ? ''
          : values
              .map((value, index) => `${(index / (values.length - 1)) * 100},${100 - ((value - min) / range) * 96 - 2}`)
              .join(' '),
    };
  }
}
