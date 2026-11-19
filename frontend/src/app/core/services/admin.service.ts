import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export interface AdminOverview {
  users: number;
  vehicles: number;
  scans: number;
  dtcCodes: number;
}

export interface AdminUser {
  id: string;
  displayName: string;
  email: string;
  roles: string[];
  vehicles: number;
  scans: number;
  joinedAt: string;
}

export interface AdminScan {
  id: string;
  scannedAt: string;
  user: string;
  vehicle: string;
  vin: string | null;
  codes: string[];
  status: 'Completed' | 'Failed';
}

@Service()
export class AdminApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/admin`;

  overview(): Observable<AdminOverview> {
    return this.http.get<AdminOverview>(`${this.url}/overview`);
  }

  listUsers(search = ''): Observable<AdminUser[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.http.get<AdminUser[]>(`${this.url}/users${query}`);
  }

  listScans(search = ''): Observable<AdminScan[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.http.get<AdminScan[]>(`${this.url}/scans${query}`);
  }

  deleteUser(id: string): Observable<void> {
    return this.http.delete<void>(`${this.url}/users/${id}`);
  }

  toggleRole(id: string): Observable<AdminUser> {
    return this.http.post<AdminUser>(`${this.url}/users/${id}/toggle-role`, {});
  }
}
