import { HttpClient } from '@angular/common/http';
import { computed, Injectable, inject, signal } from '@angular/core';

export type NotificationSeverity = 'critical' | 'warning' | 'info';

interface ApiNotification {
  id: number;
  title: string;
  detail: string;
  createdAt: string;
  severity: NotificationSeverity;
  icon: string;
  route: string;
  read: boolean;
}

export interface AppNotification extends Omit<ApiNotification, 'createdAt'> {
  time: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly notificationsSignal = signal<AppNotification[]>([]);

  readonly notifications = computed(() => this.notificationsSignal());
  readonly unreadCount = computed(() => this.notificationsSignal().filter(item => !item.read).length);

  load(): void {
    this.http.get<ApiNotification[]>(`${this.apiUrl}/notifications`).subscribe(items => {
      this.notificationsSignal.set(items.map(item => ({ ...item, time: this.relativeTime(item.createdAt) })));
    });
  }

  toggleRead(id: number): void {
    const item = this.notificationsSignal().find(notification => notification.id === id);
    if (!item) {
      return;
    }
    this.setRead(id, !item.read);
  }

  markRead(id: number): void {
    const item = this.notificationsSignal().find(notification => notification.id === id);
    if (item && !item.read) {
      this.setRead(id, true);
    }
  }

  markAllRead(): void {
    this.http.post(`${this.apiUrl}/notifications/mark-all-read`, {}).subscribe(() => {
      this.notificationsSignal.update(items => items.map(item => ({ ...item, read: true })));
    });
  }

  deleteNotification(id: number): void {
    this.http.delete(`${this.apiUrl}/notifications/${id}`).subscribe(() => {
      this.notificationsSignal.update(items => items.filter(item => item.id !== id));
    });
  }

  clearAll(): void {
    this.http.delete(`${this.apiUrl}/notifications`).subscribe(() => {
      this.notificationsSignal.set([]);
    });
  }

  private setRead(id: number, read: boolean): void {
    this.http.patch<ApiNotification>(`${this.apiUrl}/notifications/${id}`, { read }).subscribe(() => {
      this.notificationsSignal.update(items =>
        items.map(item => item.id === id ? { ...item, read } : item),
      );
    });
  }

  private relativeTime(value: string): string {
    const milliseconds = Date.now() - new Date(value).getTime();
    const minutes = Math.max(Math.floor(milliseconds / 60000), 0);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} min ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hr ago`;
    return new Date(value).toLocaleDateString();
  }
}
