import { Service, effect, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';
import { UnitSystem } from './obd-decoder';

const REFRESH_KEY = 'obd360_refresh_ms';
const CONFIRM_CLEAR_KEY = 'obd360_confirm_clear';

const readStored = (key: string): string | null => {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
};

const store = (key: string, value: string): void => {
  try {
    localStorage.setItem(key, value);
  } catch {
    // The setting still applies for this session.
  }
};

@Service()
export class UserSettings {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/preferences`;

  readonly unitSystem = signal<UnitSystem>('metric');
  readonly refreshMs = signal(Number(readStored(REFRESH_KEY)) || 500);
  readonly confirmClear = signal(readStored(CONFIRM_CLEAR_KEY) !== 'false');

  constructor() {
    effect(() => store(REFRESH_KEY, String(this.refreshMs())));
    effect(() => store(CONFIRM_CLEAR_KEY, String(this.confirmClear())));
  }

  load(): Observable<{ unitSystem: UnitSystem }> {
    return this.http
      .get<{ unitSystem: UnitSystem }>(this.url)
      .pipe(tap((preferences) => this.unitSystem.set(preferences.unitSystem)));
  }

  saveUnitSystem(): Observable<void> {
    return this.http.put<void>(this.url, { unitSystem: this.unitSystem() });
  }
}
