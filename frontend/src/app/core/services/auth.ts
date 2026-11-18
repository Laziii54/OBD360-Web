import { Service, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, finalize, map, of, shareReplay, tap } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';
import { AuthResponse, LoginRequest, RegisterRequest } from '../models/auth.model';

const ACCESS_TOKEN_KEY = 'obd360_access_token';
const USER_KEY = 'obd360_user';

export interface CurrentUser {
  userId: string;
  displayName: string;
  email: string;
  roles: string[];
}

@Service()
export class Auth {
  private readonly http = inject(HttpClient);

  private readonly accessTokenSignal = signal<string | null>(sessionStorage.getItem(ACCESS_TOKEN_KEY));
  private readonly userSignal = signal<CurrentUser | null>(this.readStoredUser());
  private refreshInFlight: Observable<AuthResponse> | null = null;

  readonly accessToken = this.accessTokenSignal.asReadonly();
  readonly currentUser = this.userSignal.asReadonly();
  readonly isAuthenticated = computed(() => this.accessTokenSignal() !== null);

  register(request: RegisterRequest): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${API_BASE_URL}/auth/register`, request, { withCredentials: true })
      .pipe(tap((response) => this.setSession(response)));
  }

  login(request: LoginRequest): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${API_BASE_URL}/auth/login`, request, { withCredentials: true })
      .pipe(tap((response) => this.setSession(response)));
  }

  // Parallel callers share one request, because the server rotates the refresh token.
  refresh(): Observable<AuthResponse> {
    this.refreshInFlight ??= this.http
      .post<AuthResponse>(`${API_BASE_URL}/auth/refresh`, {}, { withCredentials: true })
      .pipe(
        tap((response) => this.setSession(response)),
        finalize(() => (this.refreshInFlight = null)),
        shareReplay({ bufferSize: 1, refCount: false })
      );

    return this.refreshInFlight;
  }

  // Resolves to true when a usable access token exists, refreshing it if needed.
  ensureSession(): Observable<boolean> {
    if (this.hasValidToken()) {
      return of(true);
    }

    return this.refresh().pipe(
      map(() => true),
      catchError(() => {
        this.clearSession();
        return of(false);
      })
    );
  }

  // The local session ends even if the server cannot be reached.
  logout(): Observable<void> {
    return this.http
      .post<void>(`${API_BASE_URL}/auth/logout`, {}, { withCredentials: true })
      .pipe(
        catchError(() => of(undefined)),
        tap(() => this.clearSession())
      );
  }

  clearSession(): void {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
    this.accessTokenSignal.set(null);
    this.userSignal.set(null);
  }

  private setSession(response: AuthResponse): void {
    const user: CurrentUser = {
      userId: response.userId,
      displayName: response.displayName,
      email: response.email,
      roles: response.roles,
    };
    sessionStorage.setItem(ACCESS_TOKEN_KEY, response.accessToken);
    sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    this.accessTokenSignal.set(response.accessToken);
    this.userSignal.set(user);
  }

  private hasValidToken(): boolean {
    const token = this.accessTokenSignal();
    if (!token) {
      return false;
    }

    try {
      const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      const { exp } = JSON.parse(atob(payload)) as { exp?: number };
      return typeof exp === 'number' && exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  private readStoredUser(): CurrentUser | null {
    const raw = sessionStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as CurrentUser) : null;
  }
}
