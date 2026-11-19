import { DOCUMENT } from '@angular/common';
import {
  Component,
  DestroyRef,
  HostListener,
  computed,
  effect,
  inject,
  signal
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  NavigationEnd,
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet
} from '@angular/router';
import { filter } from 'rxjs';
import { Auth } from '../../core/services/auth';
import { ObdBluetooth } from '../../core/services/obd-bluetooth.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [
    RouterLink,
    RouterLinkActive,
    RouterOutlet
  ],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss'
})
export class MainLayout {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);
  private readonly document = inject(DOCUMENT);
  private readonly destroyRef = inject(DestroyRef);

  readonly adapter = inject(ObdBluetooth);
  readonly currentUser = this.auth.currentUser;
  readonly sidebarOpen = signal(false);

  constructor() {
    effect(() => {
      this.document.body.style.overflow = this.sidebarOpen() ? 'hidden' : '';
    });

    this.router.events
      .pipe(
        filter((event) => event instanceof NavigationEnd),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(() => this.closeSidebar());
  }

  toggleSidebar(): void {
    this.sidebarOpen.update((open) => !open);
  }

  closeSidebar(): void {
    this.sidebarOpen.set(false);
  }

  @HostListener('window:resize')
  onResize(): void {
    if (window.innerWidth > 720 && this.sidebarOpen()) {
      this.closeSidebar();
    }
  }

  // Georgian letters are kept as they are: toUpperCase() would turn them
  // into Mtavruli capitals, which many fonts cannot display.
  readonly userInitial = computed(() => {
    const first = [...(this.currentUser()?.displayName.trim() ?? '')][0] ?? 'U';
    return /[a-z]/.test(first) ? first.toUpperCase() : first;
  });

  readonly userRole = computed(() =>
    this.currentUser()?.roles.includes('Admin') ? 'Administrator' : 'Standard Account'
  );

  readonly isAdmin = computed(() =>
    this.currentUser()?.roles.includes('Admin') ?? false
  );

  logout(): void {
    this.auth.logout().subscribe(() => this.router.navigateByUrl('/login'));
  }
}
