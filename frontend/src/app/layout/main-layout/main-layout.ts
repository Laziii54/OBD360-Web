import { Component, computed, inject } from '@angular/core';
import {
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet
} from '@angular/router';
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

  readonly adapter = inject(ObdBluetooth);
  readonly currentUser = this.auth.currentUser;

  // Georgian letters are kept as they are: toUpperCase() would turn them
  // into Mtavruli capitals, which many fonts cannot display.
  readonly userInitial = computed(() => {
    const first = [...(this.currentUser()?.displayName.trim() ?? '')][0] ?? 'U';
    return /[a-z]/.test(first) ? first.toUpperCase() : first;
  });

  readonly userRole = computed(() =>
    this.currentUser()?.roles.includes('Admin') ? 'Administrator' : 'Standard Account'
  );

  logout(): void {
    this.auth.logout().subscribe(() => this.router.navigateByUrl('/login'));
  }
}
