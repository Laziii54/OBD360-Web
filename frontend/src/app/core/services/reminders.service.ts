import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export type ReminderStatus = 'pending' | 'overdue' | 'done';

export interface Reminder {
  id: string;
  vehicleId: string;
  vehicle: string;
  type: string;
  dueAtKm: number | null;
  dueAtDate: string | null;
  status: ReminderStatus;
}

export interface ReminderInput {
  vehicleId: string;
  type: string;
  dueAtKm: number | null;
  dueAtDate: string | null;
}

@Service()
export class RemindersApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/reminders`;

  list(vehicleId: string | null = null): Observable<Reminder[]> {
    const query = vehicleId ? `?vehicleId=${vehicleId}` : '';
    return this.http.get<Reminder[]>(`${this.url}${query}`);
  }

  create(input: ReminderInput): Observable<Reminder> {
    return this.http.post<Reminder>(this.url, input);
  }

  update(id: string, input: ReminderInput): Observable<void> {
    return this.http.put<void>(`${this.url}/${id}`, input);
  }

  complete(id: string): Observable<void> {
    return this.http.post<void>(`${this.url}/${id}/complete`, {});
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
