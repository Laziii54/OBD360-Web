import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toObservable } from '@angular/core/rxjs-interop';
import { catchError, debounceTime, of, switchMap, tap } from 'rxjs';
import {
  DtcCatalogDetail,
  DtcCatalogListItem,
  DtcLanguage,
  DtcLocalizedText,
  PagedResult,
} from '../../core/models/dtc-catalog.model';
import { DtcCatalogApi } from '../../core/services/dtc-catalog.service';

const LABELS = {
  ka: {
    subtitle: 'მოძებნე შეცდომის კოდი, მიზეზები და სიმპტომები.',
    search: 'კოდი ან აღწერა, მაგ. P0300',
    all: 'ყველა',
    powertrain: 'ძრავი',
    chassis: 'შასი',
    body: 'ძარა',
    network: 'ქსელი',
    results: 'შედეგი',
    loading: 'იტვირთება...',
    empty: 'ვერაფერი მოიძებნა.',
    failed: 'კატალოგი ვერ ჩაიტვირთა. შეამოწმე, გაშვებულია თუ არა ბექენდი.',
    previous: 'წინა',
    next: 'შემდეგი',
    close: 'დახურვა',
    causes: 'შესაძლო მიზეზები',
    symptoms: 'სიმპტომები',
    components: 'კომპონენტები',
    repair: 'შეკეთება',
    difficulty: 'სირთულე',
    cost: 'ფასი',
    hours: 'დრო',
    diy: 'თავად შეკეთება',
    yes: 'შესაძლებელია',
    no: 'არ არის რეკომენდებული',
    related: 'დაკავშირებული კოდები',
    sources: 'წყაროები',
    easy: 'მარტივი',
    medium: 'საშუალო',
    hard: 'რთული',
    shop_only: 'მხოლოდ სერვისში',
    unknown: 'უცნობი',
    high: 'მაღალი',
    low: 'დაბალი',
  },
  en: {
    subtitle: 'Search trouble codes, causes and symptoms.',
    search: 'Code or description, e.g. P0300',
    all: 'All',
    powertrain: 'Powertrain',
    chassis: 'Chassis',
    body: 'Body',
    network: 'Network',
    results: 'results',
    loading: 'Loading...',
    empty: 'Nothing found.',
    failed: 'The catalog could not be loaded. Check that the backend is running.',
    previous: 'Previous',
    next: 'Next',
    close: 'Close',
    causes: 'Possible causes',
    symptoms: 'Symptoms',
    components: 'Components',
    repair: 'Repair',
    difficulty: 'Difficulty',
    cost: 'Cost',
    hours: 'Time',
    diy: 'DIY repair',
    yes: 'Possible',
    no: 'Not recommended',
    related: 'Related codes',
    sources: 'Sources',
    easy: 'Easy',
    medium: 'Medium',
    hard: 'Hard',
    shop_only: 'Shop only',
    unknown: 'Unknown',
    high: 'High',
    low: 'Low',
  },
} as const;

type LabelKey = keyof typeof LABELS.en;

@Component({
  imports: [],
  selector: 'app-dtc-catalog',
  styleUrl: './dtc-catalog.scss',
  templateUrl: './dtc-catalog.html',
})
export class DtcCatalog {
  private readonly api = inject(DtcCatalogApi);

  readonly categories = ['', 'powertrain', 'chassis', 'body', 'network'] as const;

  readonly language = signal<DtcLanguage>('ka');
  readonly search = signal('');
  readonly category = signal('');
  readonly page = signal(1);

  readonly loading = signal(true);
  readonly failed = signal(false);
  readonly result = signal<PagedResult<DtcCatalogListItem> | null>(null);
  readonly selected = signal<DtcCatalogDetail | null>(null);

  readonly labels = computed(() => LABELS[this.language()]);
  readonly totalPages = computed(() => {
    const result = this.result();
    return result ? Math.max(Math.ceil(result.total / result.pageSize), 1) : 1;
  });

  private readonly query = computed(() => ({
    search: this.search(),
    category: this.category(),
    page: this.page(),
  }));

  constructor() {
    toObservable(this.query)
      .pipe(
        debounceTime(250),
        tap(() => {
          this.loading.set(true);
          this.failed.set(false);
        }),
        switchMap((query) =>
          this.api.list(query).pipe(
            catchError(() => {
              this.failed.set(true);
              return of(null);
            })
          )
        ),
        takeUntilDestroyed()
      )
      .subscribe((result) => {
        this.result.set(result);
        this.loading.set(false);
      });
  }

  onSearch(value: string): void {
    this.search.set(value);
    this.page.set(1);
  }

  selectCategory(category: string): void {
    this.category.set(category);
    this.page.set(1);
  }

  open(code: string): void {
    this.api.get(code).subscribe({
      next: (detail) => this.selected.set(detail),
      error: () => this.failed.set(true),
    });
  }

  close(): void {
    this.selected.set(null);
  }

  label(key: string): string {
    return this.labels()[key as LabelKey] ?? key;
  }

  title(item: DtcCatalogListItem): string {
    return this.language() === 'ka' ? item.titleKa : item.titleEn;
  }

  description(item: DtcCatalogDetail): string {
    return this.language() === 'ka' ? item.descriptionKa : item.descriptionEn;
  }

  text(item: DtcLocalizedText): string {
    return item[this.language()];
  }

  componentName(id: string): string {
    return id.replace(/_/g, ' ');
  }
}
