import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DtcScanner } from './dtc-scanner';

describe('DtcScanner', () => {
  let component: DtcScanner;
  let fixture: ComponentFixture<DtcScanner>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DtcScanner],
      providers: [provideHttpClient()],
    }).compileComponents();

    fixture = TestBed.createComponent(DtcScanner);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
