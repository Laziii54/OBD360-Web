import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export interface AiReportCode {
  code: string;
  title: string;
  description: string;
}

export interface AiScanReport {
  vehicle: string;
  scannedAt: string;
  hasProblems: boolean;
  codes: AiReportCode[];
  explanation: string | null;
  aiError: string | null;
}

export type AiMessageRole = 'user' | 'assistant';

export interface AiAskResponse {
  conversationId: string | null;
  answer: string | null;
  error: string | null;
}

export interface AiConversationMessage {
  role: AiMessageRole;
  content: string;
  createdAt: string;
}

export interface AiConversation {
  id: string;
  createdAt: string;
  messages: AiConversationMessage[];
}

export interface AiIntegrationStatus {
  configured: boolean;
  reachable: boolean | null;
  scanReportConfigured: boolean;
  askConfigured: boolean;
  workflows: string[];
  message: string | null;
}

export type AiIntegrationState = 'online' | 'offline' | 'unknown';

export const aiIntegrationState = (status: AiIntegrationStatus | null): AiIntegrationState => {
  if (!status || !status.configured || status.reachable === false) {
    return 'offline';
  }

  return status.reachable === true ? 'online' : 'unknown';
};

export const aiIntegrationLabel = (status: AiIntegrationStatus | null): string => {
  if (!status) {
    return 'n8n სტატუსი მიუწვდომელია';
  }

  if (!status.configured) {
    return 'n8n არ არის კონფიგურირებული';
  }

  if (status.reachable === false) {
    return 'n8n მიუწვდომელია';
  }

  return status.reachable === true ? 'n8n დაკავშირებულია' : 'n8n კონფიგურირებულია';
};

@Service()
export class AiReportApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/ai`;

  latestScanReport(): Observable<AiScanReport> {
    return this.http.post<AiScanReport>(`${this.url}/latest-scan-report`, {});
  }

  status(): Observable<AiIntegrationStatus> {
    return this.http.get<AiIntegrationStatus>(`${this.url}/status`);
  }

  latestConversation(): Observable<AiConversation | null> {
    return this.http.get<AiConversation | null>(`${this.url}/conversation`);
  }

  ask(question: string, conversationId: string | null): Observable<AiAskResponse> {
    return this.http.post<AiAskResponse>(`${this.url}/ask`, { question, conversationId });
  }
}
