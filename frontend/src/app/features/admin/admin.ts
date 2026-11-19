import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import {
  AdminApi,
  AdminOverview,
  AdminScan,
  AdminUser,
} from '../../core/services/admin.service';

type AdminTab = 'overview' | 'users' | 'scans';

@Component({
  imports: [DatePipe],
  selector: 'app-admin',
  styleUrl: './admin.scss',
  templateUrl: './admin.html',
})
export class Admin {
  private readonly api = inject(AdminApi);

  readonly tab = signal<AdminTab>('overview');
  readonly overview = signal<AdminOverview | null>(null);
  readonly users = signal<AdminUser[]>([]);
  readonly scans = signal<AdminScan[]>([]);
  readonly userSearch = signal('');
  readonly scanSearch = signal('');
  readonly toast = signal<string | null>(null);
  readonly loading = signal(true);
  readonly errorMessage = signal<string | null>(null);

  readonly filteredUsers = computed(() => {
    const term = this.userSearch().trim().toLowerCase();

    return this.users().filter(
      (user) =>
        !term ||
        user.displayName.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term) ||
        user.roles.some((role) => role.toLowerCase().includes(term))
    );
  });

  readonly filteredScans = computed(() => {
    const term = this.scanSearch().trim().toLowerCase();

    return this.scans().filter(
      (scan) =>
        !term ||
        scan.user.toLowerCase().includes(term) ||
        scan.vehicle.toLowerCase().includes(term) ||
        scan.vin?.toLowerCase().includes(term) ||
        scan.codes.some((code) => code.toLowerCase().includes(term))
    );
  });

  readonly recentUsers = computed(() => this.users().slice(0, 4));
  readonly recentScans = computed(() => this.scans().slice(0, 4));

  constructor() {
    this.reload();
  }

  setTab(tab: AdminTab): void {
    this.tab.set(tab);
  }

  reload(): void {
    this.loading.set(true);
    this.errorMessage.set(null);

    forkJoin({
      overview: this.api.overview(),
      users: this.api.listUsers(),
      scans: this.api.listScans(),
    }).subscribe({
      next: ({ overview, users, scans }) => {
        this.overview.set(overview);
        this.users.set(users);
        this.scans.set(scans);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.errorMessage.set('ადმინის მონაცემები ვერ ჩაიტვირთა.');
      },
    });
  }

  deleteUser(user: AdminUser): void {
    const confirmed = confirm(
      `წავშალო მომხმარებელი ${user.displayName}? ელფოსტა ${user.email} და მისი მონაცემებიც წაიშლება.`
    );

    if (!confirmed) {
      return;
    }

    this.api.deleteUser(user.id).subscribe({
      next: () => {
        this.showToast('მომხმარებელი წაშლილია.');
        this.reload();
      },
      error: () => this.showToast('მომხმარებლის წაშლა ვერ მოხდა.'),
    });
  }

  toggleRole(user: AdminUser): void {
    this.api.toggleRole(user.id).subscribe({
      next: (updated) => {
        this.users.set(
          this.users().map((item) => (item.id === updated.id ? updated : item))
        );
        this.showToast(
          updated.roles.includes('Admin')
            ? `${updated.displayName} ახლა Admin-ია.`
            : `${updated.displayName} ახლა User-ია.`
        );
      },
      error: () => this.showToast('როლის შეცვლა ვერ მოხდა.'),
    });
  }

  private showToast(message: string): void {
    this.toast.set(message);
    setTimeout(() => this.toast.set(null), 2600);
  }
}
