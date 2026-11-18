import { Service, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';
import {
  DtcCatalogDetail,
  DtcCatalogListItem,
  DtcCatalogQuery,
  PagedResult,
} from '../models/dtc-catalog.model';

@Service()
export class DtcCatalogApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${API_BASE_URL}/dtc-catalog`;

  list(query: DtcCatalogQuery): Observable<PagedResult<DtcCatalogListItem>> {
    const params = new HttpParams()
      .set('search', query.search.trim())
      .set('category', query.category)
      .set('page', query.page);

    return this.http.get<PagedResult<DtcCatalogListItem>>(this.baseUrl, { params });
  }

  get(code: string): Observable<DtcCatalogDetail> {
    return this.http.get<DtcCatalogDetail>(`${this.baseUrl}/${encodeURIComponent(code)}`);
  }
}
