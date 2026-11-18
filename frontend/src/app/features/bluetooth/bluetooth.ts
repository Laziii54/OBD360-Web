import { Component, computed, inject } from '@angular/core';
import { ObdBluetooth } from '../../core/services/obd-bluetooth.service';

const STATUS_LABELS = {
  disconnected: 'Disconnected',
  connecting: 'Connecting...',
  initializing: 'Initializing...',
  connected: 'Connected',
} as const;

@Component({
  imports: [],
  selector: 'app-bluetooth',
  styleUrl: './bluetooth.scss',
  templateUrl: './bluetooth.html',
})
export class Bluetooth {
  readonly adapter = inject(ObdBluetooth);

  readonly statusLabel = computed(() => STATUS_LABELS[this.adapter.status()]);

  toggleConnection(): void {
    if (this.adapter.isConnected()) {
      this.adapter.disconnect();
    } else {
      void this.adapter.connect();
    }
  }
}
