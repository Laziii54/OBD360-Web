import { Service } from '@angular/core';
import { Observable, of } from 'rxjs';

export type AdminRole = 'Admin' | 'User';

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: AdminRole;
  vehicles: number;
  scans: number;
  joinedAt: string;
}

export interface AdminScan {
  id: string;
  scannedAt: string;
  user: string;
  vehicle: string;
  vin: string;
  codes: string[];
  status: 'Completed' | 'Failed';
}

/**
 * Frontend-only admin prototype.
 * Replace these arrays with HTTP calls when the admin API is added.
 */
@Service()
export class AdminApi {
  private users: AdminUser[] = [
    {
      id: 'u-1',
      name: 'Nino Beridze',
      email: 'nino.beridze@gmail.com',
      role: 'User',
      vehicles: 2,
      scans: 14,
      joinedAt: '2026-09-12T10:20:00Z',
    },
    {
      id: 'u-2',
      name: 'Giorgi Kapanadze',
      email: 'g.kapanadze@gmail.com',
      role: 'User',
      vehicles: 1,
      scans: 8,
      joinedAt: '2026-09-28T16:40:00Z',
    },
    {
      id: 'u-3',
      name: 'Salome Tsiklauri',
      email: 'salome.ts@gmail.com',
      role: 'Admin',
      vehicles: 3,
      scans: 31,
      joinedAt: '2026-08-04T09:15:00Z',
    },
    {
      id: 'u-4',
      name: 'Luka Maisuradze',
      email: 'luka.maisuradze@gmail.com',
      role: 'User',
      vehicles: 1,
      scans: 5,
      joinedAt: '2026-10-19T12:05:00Z',
    },
    {
      id: 'u-5',
      name: 'Ana Kharadze',
      email: 'ana.kharadze@gmail.com',
      role: 'User',
      vehicles: 2,
      scans: 19,
      joinedAt: '2026-10-30T18:30:00Z',
    },
    {
      id: 'u-6',
      name: 'Zurab Lazashvili',
      email: 'obd360sup@gmail.com',
      role: 'Admin',
      vehicles: 1,
      scans: 7,
      joinedAt: '2026-11-19T13:00:00Z',
    },
  ];

  private scans: AdminScan[] = [
    {
      id: 's-1',
      scannedAt: '2026-11-19T14:32:00Z',
      user: 'Nino Beridze',
      vehicle: 'Chevrolet Volt 2013',
      vin: '1G1RB6E42DU101631',
      codes: ['P0A80', 'P0300'],
      status: 'Completed',
    },
    {
      id: 's-2',
      scannedAt: '2026-11-19T12:10:00Z',
      user: 'Giorgi Kapanadze',
      vehicle: 'Toyota Camry 2020',
      vin: '4T1BF1FK5CU123456',
      codes: ['P0420'],
      status: 'Completed',
    },
    {
      id: 's-3',
      scannedAt: '2026-11-18T18:05:00Z',
      user: 'Ana Kharadze',
      vehicle: 'Honda Civic 2018',
      vin: '19XFC2F59JE000123',
      codes: [],
      status: 'Completed',
    },
    {
      id: 's-4',
      scannedAt: '2026-11-18T09:42:00Z',
      user: 'Zurab Lazashvili',
      vehicle: 'Chevrolet Volt 2012',
      vin: '1G1RB6E42DU101631',
      codes: ['P0171'],
      status: 'Completed',
    },
    {
      id: 's-5',
      scannedAt: '2026-11-17T20:18:00Z',
      user: 'Luka Maisuradze',
      vehicle: 'BMW 320d 2016',
      vin: 'WBA8E9G50GNT12345',
      codes: ['P0299', 'P2002'],
      status: 'Failed',
    },
    {
      id: 's-6',
      scannedAt: '2026-11-17T15:55:00Z',
      user: 'Salome Tsiklauri',
      vehicle: 'Audi A4 2019',
      vin: 'WAUENAF47JA123456',
      codes: [],
      status: 'Completed',
    },
  ];

  readonly dtcCodeCount = 13629;

  listUsers(): Observable<AdminUser[]> {
    return of(this.users.map((user) => ({ ...user })));
  }

  listScans(): Observable<AdminScan[]> {
    return of(this.scans.map((scan) => ({ ...scan })));
  }

  deleteUser(id: string): Observable<void> {
    this.users = this.users.filter((user) => user.id !== id);
    return of(void 0);
  }

  toggleRole(id: string): Observable<AdminUser | null> {
    const user = this.users.find((item) => item.id === id);
    if (!user) {
      return of(null);
    }

    user.role = user.role === 'Admin' ? 'User' : 'Admin';
    return of({ ...user });
  }
}
