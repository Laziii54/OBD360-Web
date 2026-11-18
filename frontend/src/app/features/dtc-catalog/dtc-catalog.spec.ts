import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DtcCatalog } from './dtc-catalog';

describe('DtcCatalog', () => {
  let component: DtcCatalog;
  let fixture: ComponentFixture<DtcCatalog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DtcCatalog],
      providers: [provideHttpClient()],
    }).compileComponents();

    fixture = TestBed.createComponent(DtcCatalog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
