import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { FreezeFrame } from './freeze-frame';

describe('FreezeFrame', () => {
  let component: FreezeFrame;
  let fixture: ComponentFixture<FreezeFrame>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FreezeFrame],
      providers: [provideHttpClient(), provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(FreezeFrame);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
