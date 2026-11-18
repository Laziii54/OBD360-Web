import { Component, computed, inject, signal } from '@angular/core';
import { Auth } from '../../core/services/auth';
import { UnitSystem } from '../../core/services/obd-decoder';
import {
  AiIntegrationStatus,
  AiReportApi,
  aiIntegrationLabel,
  aiIntegrationState,
} from '../../core/services/ai-report.service';
import { UserSettings } from '../../core/services/user-settings.service';

@Component({
  imports: [],
  selector: 'app-settings',
  styleUrl: './settings.scss',
  templateUrl: './settings.html',
})
export class Settings {
  private readonly auth = inject(Auth);
  private readonly aiApi = inject(AiReportApi);

  readonly settings = inject(UserSettings);
  readonly currentUser = this.auth.currentUser;
  readonly refreshRates = [250, 500, 1000, 2000];

  readonly saveState = signal<'idle' | 'saving' | 'saved' | 'failed'>('idle');
  readonly integration = signal<AiIntegrationStatus | null>(null);

  readonly integrationState = computed(() => aiIntegrationState(this.integration()));
  readonly integrationLabel = computed(() => aiIntegrationLabel(this.integration()));

  readonly integrationDetail = computed(() => {
    const status = this.integration();
    if (!status) {
      return 'n8n-ის სტატუსი ვერ მიიღო. სცადე ხელახლა.';
    }

    if (!status.configured) {
      return 'N8n:BaseUrl ცარიელია — მიუთითე appsettings-ში ან user secrets-ში.';
    }

    if (status.reachable === false) {
      return 'n8n სერვერი არ პასუხობს. შეამოწმე, გაშვებულია თუ არა ინსტანსი.';
    }

    if (status.reachable === null) {
      return 'n8n კონფიგურირებულია, მაგრამ მისამართის შემოწმება ვერ მოხდა.';
    }

    return 'n8n პასუხობს და workflow-ები კონფიგურირებულია.';
  });

  readonly userInitial = computed(() => {
    const first = [...(this.currentUser()?.displayName.trim() ?? '')][0] ?? 'U';
    return /[a-z]/.test(first) ? first.toUpperCase() : first;
  });

  constructor() {
    this.settings.load().subscribe({ error: () => this.saveState.set('failed') });
    this.checkIntegration();
  }

  setUnitSystem(value: string): void {
    this.settings.unitSystem.set(value as UnitSystem);
    this.saveState.set('saving');

    this.settings.saveUnitSystem().subscribe({
      next: () => this.saveState.set('saved'),
      error: () => this.saveState.set('failed'),
    });
  }

  checkIntegration(): void {
    this.aiApi.status().subscribe({
      next: (status) => this.integration.set(status),
      error: () => this.integration.set(null),
    });
  }
}
