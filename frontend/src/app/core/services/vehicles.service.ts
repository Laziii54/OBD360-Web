import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export interface Vehicle {
  id: string;
  vin: string | null;
  make: string;
  model: string;
  year: number;
  plateNumber: string | null;
  scanCount: number;
  lastScanAt: string | null;
  createdAt: string;
}

export interface VehicleInput {
  make: string;
  model: string;
  year: number;
  vin: string | null;
  plateNumber: string | null;
}

@Service()
export class VehiclesApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/vehicles`;

  list(): Observable<Vehicle[]> {
    return this.http.get<Vehicle[]>(this.url);
  }

  create(input: VehicleInput): Observable<Vehicle> {
    return this.http.post<Vehicle>(this.url, input);
  }

  update(id: string, input: VehicleInput): Observable<void> {
    return this.http.put<void>(`${this.url}/${id}`, input);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
