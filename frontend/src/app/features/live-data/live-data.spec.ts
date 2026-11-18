import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LiveData } from './live-data';

describe('LiveData', () => {
  let component: LiveData;
  let fixture: ComponentFixture<LiveData>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LiveData],
      providers: [provideHttpClient(), provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(LiveData);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
