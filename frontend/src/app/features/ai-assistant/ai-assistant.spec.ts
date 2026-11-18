import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { AiAssistant } from './ai-assistant';

describe('AiAssistant', () => {
  it('should create', async () => {
    await TestBed.configureTestingModule({
      imports: [AiAssistant],
      providers: [provideHttpClient()],
    }).compileComponents();

    expect(TestBed.createComponent(AiAssistant).componentInstance).toBeTruthy();
  });
});
