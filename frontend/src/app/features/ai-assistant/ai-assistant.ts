import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import {
  AiConversationMessage,
  AiIntegrationStatus,
  AiReportApi,
  AiScanReport,
  aiIntegrationLabel,
  aiIntegrationState,
} from '../../core/services/ai-report.service';

@Component({
  imports: [DatePipe],
  selector: 'app-ai-assistant',
  styleUrl: './ai-assistant.scss',
  templateUrl: './ai-assistant.html',
})
export class AiAssistant {
  private readonly api = inject(AiReportApi);

  readonly loading = signal(true);
  readonly noScan = signal(false);
  readonly failed = signal(false);
  readonly report = signal<AiScanReport | null>(null);

  readonly integration = signal<AiIntegrationStatus | null>(null);
  readonly messages = signal<AiConversationMessage[]>([]);
  readonly conversationId = signal<string | null>(null);
  readonly draft = signal('');
  readonly asking = signal(false);
  readonly askError = signal<string | null>(null);

  readonly integrationState = computed(() => aiIntegrationState(this.integration()));
  readonly integrationLabel = computed(() => aiIntegrationLabel(this.integration()));

  constructor() {
    this.load();
    this.loadIntegration();
    this.loadConversation();
  }

  load(): void {
    this.loading.set(true);
    this.noScan.set(false);
    this.failed.set(false);

    this.api.latestScanReport().subscribe({
      next: (report) => {
        this.report.set(report);
        this.loading.set(false);
      },
      error: (error: HttpErrorResponse) => {
        this.noScan.set(error.status === 404);
        this.failed.set(error.status !== 404);
        this.loading.set(false);
      },
    });
  }

  loadIntegration(): void {
    this.api.status().subscribe({
      next: (status) => this.integration.set(status),
      error: () => this.integration.set(null),
    });
  }

  loadConversation(): void {
    this.api.latestConversation().subscribe({
      next: (conversation) => {
        if (!conversation) {
          return;
        }

        this.conversationId.set(conversation.id);
        this.messages.set(conversation.messages);
      },
      // The history is optional: the chat simply starts empty.
      error: () => this.messages.set([]),
    });
  }

  updateDraft(value: string): void {
    this.draft.set(value);
  }

  ask(): void {
    const question = this.draft().trim();
    if (!question || this.asking()) {
      return;
    }

    this.asking.set(true);
    this.askError.set(null);

    this.api.ask(question, this.conversationId()).subscribe({
      next: (response) => {
        this.asking.set(false);
        this.conversationId.set(response.conversationId);

        const answer = response.answer;
        if (answer) {
          const createdAt = new Date().toISOString();
          this.messages.update((messages) => [
            ...messages,
            { role: 'user', content: question, createdAt },
            { role: 'assistant', content: answer, createdAt },
          ]);
          this.draft.set('');
        }

        if (response.error) {
          this.askError.set(response.error);
          this.loadIntegration();
        }
      },
      error: () => {
        this.asking.set(false);
        this.askError.set('კითხვის გაგზავნა ვერ მოხდა. შეამოწმე კავშირი და სცადე ხელახლა.');
      },
    });
  }
}
