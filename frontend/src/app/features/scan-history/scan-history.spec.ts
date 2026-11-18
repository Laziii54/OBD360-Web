import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ScanHistory } from './scan-history';

describe('ScanHistory', () => {
  let component: ScanHistory;
  let fixture: ComponentFixture<ScanHistory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScanHistory],
      providers: [provideHttpClient(), provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(ScanHistory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
