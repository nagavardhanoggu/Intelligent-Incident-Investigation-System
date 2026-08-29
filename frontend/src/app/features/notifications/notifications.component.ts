import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AppNotification, NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-notifications',
  imports: [MatButtonModule, MatCardModule, MatChipsModule, MatIconModule, MatTooltipModule],
  templateUrl: './notifications.component.html',
  styleUrl: './notifications.component.scss',
})
export class NotificationsComponent implements OnInit {
  private readonly notificationService = inject(NotificationService);
  readonly filter = signal<'all' | 'unread'>('all');
  readonly notifications = this.notificationService.notifications;
  readonly visibleNotifications = computed(() => {
    const items = this.notifications();
    return this.filter() === 'unread' ? items.filter(item => !item.read) : items;
  });
  readonly unreadCount = this.notificationService.unreadCount;

  ngOnInit(): void {
    this.notificationService.load();
  }

  severityLabel(item: AppNotification): string {
    return item.severity.charAt(0).toUpperCase() + item.severity.slice(1);
  }

  setFilter(filter: 'all' | 'unread'): void {
    this.filter.set(filter);
  }

  toggleRead(id: number): void {
    this.notificationService.toggleRead(id);
  }

  markAllRead(): void {
    this.notificationService.markAllRead();
  }

  deleteNotification(id: number): void {
    this.notificationService.deleteNotification(id);
  }

  clearAll(): void {
    this.notificationService.clearAll();
  }
}
