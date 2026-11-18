import { inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';
import { Auth } from '../services/auth';

const withToken = <T>(req: HttpRequest<T>, token: string | null): HttpRequest<T> =>
  token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(Auth);
  const router = inject(Router);

  const isApiRequest = req.url.startsWith(API_BASE_URL);
  const isAuthRequest = req.url.startsWith(`${API_BASE_URL}/auth/`);

  if (!isApiRequest || isAuthRequest) {
    return next(req);
  }

  return next(withToken(req, auth.accessToken())).pipe(
    catchError((error: unknown) => {
      if (!(error instanceof HttpErrorResponse) || error.status !== 401) {
        return throwError(() => error);
      }

      return auth.refresh().pipe(
        catchError((refreshError: unknown) => {
          auth.clearSession();
          router.navigateByUrl('/login');
          return throwError(() => refreshError);
        }),
        switchMap(() => next(withToken(req, auth.accessToken())))
      );
    })
  );
};
