import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { DtcCatalogApi } from '../../core/services/dtc-catalog.service';
import {
  FREEZE_PIDS,
  PidDefinition,
  convertReading,
  decodeFreezeValue,
  parseFreezeDtc,
} from '../../core/services/obd-decoder';
import { ObdBluetooth } from '../../core/services/obd-bluetooth.service';
import { UserSettings } from '../../core/services/user-settings.service';

@Component({
  imports: [DatePipe],
  selector: 'app-freeze-frame',
  styleUrl: './freeze-frame.scss',
  templateUrl: './freeze-frame.html',
})
export class FreezeFrame {
  private readonly catalog = inject(DtcCatalogApi);
  private readonly settings = inject(UserSettings);

  readonly adapter = inject(ObdBluetooth);
  readonly pids = FREEZE_PIDS;

  readonly reading = signal(false);
  readonly frameDtc = signal<string | null>(null);
  readonly frameTitle = signal<string | null>(null);
  readonly readAt = signal<Date | null>(null);
  readonly values = signal<Record<string, number>>({});
  readonly errorMessage = signal<string | null>(null);

  readonly statusLabel = computed(() => {
    if (this.frameDtc()) {
      return 'FRAME AVAILABLE';
    }
    return this.adapter.isConnected() ? 'CONNECTED' : 'WAITING FOR CONNECTION';
  });

  async read(): Promise<void> {
    this.reading.set(true);
    this.errorMessage.set(null);
    this.values.set({});
    this.frameDtc.set(null);
    this.frameTitle.set(null);

    try {
      const code = parseFreezeDtc(await this.adapter.send('020200', 6000));
      this.readAt.set(new Date());

      if (!code) {
        this.errorMessage.set('The vehicle has no stored freeze frame.');
        return;
      }

      this.frameDtc.set(code);
      for (const definition of FREEZE_PIDS) {
        const raw = await this.adapter.send(`02${definition.pid.slice(2)}00`, 3000);
        const value = decodeFreezeValue(raw, definition);
        if (value !== null) {
          this.values.update((values) => ({ ...values, [definition.id]: value }));
        }
      }

      const detail = await firstValueFrom(this.catalog.get(code)).catch(() => null);
      this.frameTitle.set(detail?.titleKa ?? null);
    } catch (error) {
      this.errorMessage.set(error instanceof Error ? error.message : 'The freeze frame could not be read.');
    } finally {
      this.reading.set(false);
    }
  }

  display(pid: PidDefinition): string {
    const value = this.values()[pid.id];
    if (value === undefined) {
      return '--';
    }
    return convertReading(value, pid.unit, this.settings.unitSystem()).value.toFixed(pid.digits);
  }

  unit(pid: PidDefinition): string {
    return convertReading(0, pid.unit, this.settings.unitSystem()).unit;
  }
}
