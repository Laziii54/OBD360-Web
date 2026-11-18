import { Service, computed, inject, signal } from '@angular/core';
import { catchError, firstValueFrom, forkJoin, map, of } from 'rxjs';
import { DtcCatalogDetail } from '../models/dtc-catalog.model';
import { ScanHistoryApi } from './scan-history.service';
import { DtcCatalogApi } from './dtc-catalog.service';
import { DtcMode, VehicleStatus, parseDtcResponse, parseVehicleStatus, parseVin } from './obd-decoder';
import { ObdBluetooth } from './obd-bluetooth.service';

export interface DtcFinding {
  code: string;
  detail: DtcCatalogDetail | null;
}

export type DtcResults = Record<DtcMode, DtcFinding[]>;

const SCAN_TIMEOUT_MS = 10000;
const EMPTY_RESULTS: DtcResults = { '03': [], '07': [], '0A': [] };

@Service()
export class DtcScanService {
  private readonly adapter = inject(ObdBluetooth);
  private readonly catalog = inject(DtcCatalogApi);
  private readonly history = inject(ScanHistoryApi);

  readonly scanning = signal(false);
  readonly clearing = signal(false);
  readonly scannedAt = signal<Date | null>(null);
  readonly results = signal<DtcResults>(EMPTY_RESULTS);
  readonly vehicleStatus = signal<VehicleStatus | null>(null);
  readonly errorMessage = signal<string | null>(null);

  readonly hasScanned = computed(() => this.scannedAt() !== null);

  async scan(): Promise<void> {
    const startedAt = new Date().toISOString();
    this.scanning.set(true);
    this.errorMessage.set(null);

    try {
      const status = await this.adapter.send('0101', SCAN_TIMEOUT_MS);
      this.vehicleStatus.set(parseVehicleStatus(status));

      const isCan = this.adapter.isCan();
      const results: DtcResults = { '03': [], '07': [], '0A': [] };

      for (const mode of Object.keys(results) as DtcMode[]) {
        const raw = await this.adapter.send(mode, SCAN_TIMEOUT_MS);
        results[mode] = await this.describe(parseDtcResponse(raw, mode, isCan));
      }

      this.results.set(results);
      this.scannedAt.set(new Date());
      await this.saveScan(startedAt, results);
    } catch (error) {
      this.errorMessage.set(error instanceof Error ? error.message : 'The scan failed.');
    } finally {
      this.scanning.set(false);
    }
  }

  // Mode 04 also erases freeze frame data and resets the readiness monitors.
  async clearCodes(): Promise<void> {
    this.clearing.set(true);
    this.errorMessage.set(null);

    try {
      const response = await this.adapter.send('04', SCAN_TIMEOUT_MS);
      if (!response.replace(/\s/g, '').toUpperCase().includes('44')) {
        throw new Error('The vehicle did not confirm clearing the codes.');
      }
      await this.scan();
    } catch (error) {
      this.errorMessage.set(error instanceof Error ? error.message : 'The codes could not be cleared.');
    } finally {
      this.clearing.set(false);
    }
  }

  private async saveScan(startedAt: string, results: DtcResults): Promise<void> {
    const vin = await this.adapter.send('0902', SCAN_TIMEOUT_MS).then(parseVin).catch(() => null);
    const codes = [...new Set(Object.values(results).flat().map((finding) => finding.code))];

    try {
      await firstValueFrom(this.history.save({ vin, startedAt, codes }));
    } catch {
      this.errorMessage.set('The scan finished, but it could not be saved to history.');
    }
  }

  private describe(codes: string[]): Promise<DtcFinding[]> {
    if (!codes.length) {
      return Promise.resolve([]);
    }

    return firstValueFrom(
      forkJoin(
        codes.map((code) =>
          this.catalog.get(code).pipe(
            map((detail) => ({ code, detail })),
            catchError(() => of({ code, detail: null }))
          )
        )
      )
    );
  }
}
