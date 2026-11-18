import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EcuModules } from './ecu-modules';

describe('EcuModules', () => {
  let component: EcuModules;
  let fixture: ComponentFixture<EcuModules>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EcuModules],
    }).compileComponents();

    fixture = TestBed.createComponent(EcuModules);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
