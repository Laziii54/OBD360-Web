export type DtcLanguage = 'ka' | 'en';

export interface DtcCatalogQuery {
  search: string;
  category: string;
  page: number;
}

export interface DtcCatalogListItem {
  code: string;
  category: string;
  titleEn: string;
  titleKa: string;
  difficulty: string;
}

export interface PagedResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface DtcLocalizedText {
  en: string;
  ka: string;
}

export interface DtcCause extends DtcLocalizedText {
  likelihood: 'high' | 'medium' | 'low';
}

export interface DtcCatalogDetails {
  affectedComponents: string[];
  causes: DtcCause[];
  symptoms: DtcLocalizedText[];
  flags: {
    mil: boolean;
    emissionsRelevant: boolean;
    driveCycleRequired: boolean;
    limpModePossible: boolean;
  };
  relatedCodes: string[];
  references: string[];
  sources: string[];
}

export interface DtcCatalogDetail extends DtcCatalogListItem {
  descriptionEn: string;
  descriptionKa: string;
  diyPossible: boolean;
  estimatedCostMin: number | null;
  estimatedCostMax: number | null;
  estimatedHoursMin: number | null;
  estimatedHoursMax: number | null;
  details: DtcCatalogDetails;
}
