import { Service, computed, inject, signal } from '@angular/core';
import { LIVE_PIDS, decodePid } from './obd-decoder';
import { ObdBluetooth } from './obd-bluetooth.service';
import { UserSettings } from './user-settings.service';

export interface LiveReading {
  value: number;
  history: number[];
}

const HISTORY_LENGTH = 60;
const PID_TIMEOUT_MS = 2500;
const NO_DATA_LIMIT = 2;

const wait = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

@Service()
export class LiveDataService {
  private readonly adapter = inject(ObdBluetooth);
  private readonly settings = inject(UserSettings);
  private readonly failures = new Map<string, number>();
  private runId = 0;

  readonly refreshMs = this.settings.refreshMs;
  readonly paused = signal(false);
  readonly streaming = signal(false);
  readonly readings = signal<Record<string, LiveReading>>({});
  readonly unsupported = signal<ReadonlySet<string>>(new Set());

  readonly hasData = computed(() => Object.keys(this.readings()).length > 0);

  start(): void {
    if (!this.streaming()) {
      this.streaming.set(true);
      void this.poll(++this.runId);
    }
  }

  stop(): void {
    this.runId++;
    this.streaming.set(false);
  }

  clear(): void {
    this.readings.set({});
    this.unsupported.set(new Set());
    this.failures.clear();
  }

  private async poll(id: number): Promise<void> {
    while (id === this.runId) {
      if (!this.paused()) {
        for (const definition of LIVE_PIDS) {
          if (id !== this.runId || this.paused()) {
            break;
          }

          if (this.unsupported().has(definition.id)) {
            continue;
          }

          try {
            const raw = await this.adapter.send(definition.pid, PID_TIMEOUT_MS);
            if (id !== this.runId) {
              return;
            }

            const value = decodePid(raw, definition);
            if (value === null) {
              this.markFailure(definition.id);
            } else {
              this.record(definition.id, value);
            }
          } catch {
            if (!this.adapter.isConnected()) {
              this.stop();
              return;
            }
          }
        }
      }

      await wait(this.refreshMs());
    }
  }

  private record(id: string, value: number): void {
    this.failures.delete(id);
    this.readings.update((readings) => ({
      ...readings,
      [id]: {
        value,
        history: [...(readings[id]?.history ?? []), value].slice(-HISTORY_LENGTH),
      },
    }));
  }

  private markFailure(id: string): void {
    const failures = (this.failures.get(id) ?? 0) + 1;
    this.failures.set(id, failures);

    if (failures >= NO_DATA_LIMIT && !this.readings()[id]) {
      this.unsupported.update((ids) => new Set(ids).add(id));
    }
  }
}
