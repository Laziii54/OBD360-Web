import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export interface ScanRecord {
  id: string;
  vehicle: string;
  vin: string | null;
  startedAt: string;
  endedAt: string | null;
  codes: string[];
}

export interface NewScan {
  vin: string | null;
  startedAt: string;
  codes: string[];
}

@Service()
export class ScanHistoryApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/scans`;

  list(): Observable<ScanRecord[]> {
    return this.http.get<ScanRecord[]>(this.url);
  }

  save(scan: NewScan): Observable<void> {
    return this.http.post<void>(this.url, scan);
  }
}
