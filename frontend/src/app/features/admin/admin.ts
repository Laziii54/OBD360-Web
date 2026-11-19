import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { AdminApi, AdminScan, AdminUser } from '../../core/services/admin.service';

type AdminTab = 'overview' | 'users' | 'scans';

@Component({
  imports: [DatePipe],
  selector: 'app-admin',
  styleUrl: './admin.scss',
  templateUrl: './admin.html',
})
export class Admin {
  private readonly api = inject(AdminApi);

  readonly dtcCodeCount = this.api.dtcCodeCount;
  readonly tab = signal<AdminTab>('overview');
  readonly users = signal<AdminUser[]>([]);
  readonly scans = signal<AdminScan[]>([]);
  readonly userSearch = signal('');
  readonly scanSearch = signal('');
  readonly toast = signal<string | null>(null);

  readonly filteredUsers = computed(() => {
    const term = this.userSearch().trim().toLowerCase();

    return this.users().filter(
      (user) =>
        !term ||
        user.name.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term) ||
        user.role.toLowerCase().includes(term)
    );
  });

  readonly filteredScans = computed(() => {
    const term = this.scanSearch().trim().toLowerCase();

    return this.scans().filter(
      (scan) =>
        !term ||
        scan.user.toLowerCase().includes(term) ||
        scan.vehicle.toLowerCase().includes(term) ||
        scan.vin.toLowerCase().includes(term) ||
        scan.codes.some((code) => code.toLowerCase().includes(term))
    );
  });

  readonly totalVehicles = computed(() =>
    this.users().reduce((sum, user) => sum + user.vehicles, 0)
  );

  readonly totalScans = computed(() =>
    this.users().reduce((sum, user) => sum + user.scans, 0)
  );

  readonly recentUsers = computed(() => this.users().slice(0, 4));
  readonly recentScans = computed(() => this.scans().slice(0, 4));

  constructor() {
    this.reload();
  }

  setTab(tab: AdminTab): void {
    this.tab.set(tab);
  }

  reload(): void {
    this.api.listUsers().subscribe((users) => this.users.set(users));
    this.api.listScans().subscribe((scans) => this.scans.set(scans));
  }

  deleteUser(user: AdminUser): void {
    const confirmed = confirm(
      `წავშალო მომხმარებელი ${user.name}? ელფოსტა ${user.email} და მისი მონაცემებიც წაიშლება.`
    );

    if (!confirmed) {
      return;
    }

    this.api.deleteUser(user.id).subscribe(() => {
      this.users.set(this.users().filter((item) => item.id !== user.id));
      this.showToast('მომხმარებელი წაშლილია.');
    });
  }

  toggleRole(user: AdminUser): void {
    this.api.toggleRole(user.id).subscribe((updated) => {
      if (!updated) {
        return;
      }

      this.users.set(
        this.users().map((item) => (item.id === updated.id ? updated : item))
      );
      this.showToast(
        updated.role === 'Admin'
          ? `${updated.name} ახლა Admin-ია.`
          : `${updated.name} ახლა User-ია.`
      );
    });
  }

  private showToast(message: string): void {
    this.toast.set(message);
    setTimeout(() => this.toast.set(null), 2600);
  }
}
