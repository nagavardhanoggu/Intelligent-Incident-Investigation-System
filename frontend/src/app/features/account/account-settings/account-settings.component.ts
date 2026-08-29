import { Component, OnInit, computed, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { AuthService } from '../../../core/services/auth.service';

interface AccountSettings {
  emailAlerts: boolean;
  criticalOnly: boolean;
  weeklyDigest: boolean;
  browserPush: boolean;
  mfaEnabled: boolean;
  autoAssign: boolean;
  compactWorkspace: boolean;
  auditExports: boolean;
  jwtSessionExpiry: string;
  activeSessions: number;
  alertChannels: number;
}

@Component({
  selector: 'app-account-settings',
  imports: [FormsModule, MatButtonModule, MatCardModule, MatChipsModule, MatIconModule, MatSnackBarModule, MatSlideToggleModule],
  templateUrl: './account-settings.component.html',
  styleUrl: './account-settings.component.scss',
})
export class AccountSettingsComponent implements OnInit {
  private readonly apiUrl = 'http://localhost:8000/api/v1';

  emailAlerts = true;
  criticalOnly = false;
  weeklyDigest = true;
  mfaEnabled = true;
  browserPush = true;
  autoAssign = false;
  compactWorkspace = true;
  auditExports = true;
  saving = false;
  readonly settings = signal<AccountSettings | null>(null);

  readonly summary = computed(() => {
    const settings = this.settings();
    return [
      { label: 'Security Score', value: this.mfaEnabled ? '92%' : '74%', icon: 'security', state: this.mfaEnabled ? 'healthy' : 'watch' },
      { label: 'Active Sessions', value: String(settings?.activeSessions ?? 1), icon: 'devices', state: 'watch' },
      { label: 'Alert Channels', value: String(settings?.alertChannels ?? 4), icon: 'notifications', state: 'healthy' },
    ];
  });

  readonly sessions = computed(() => [
    {
      device: this.browserName(),
      location: 'Current browser',
      lastSeen: 'Active now',
      current: true,
    },
  ]);

  readonly securityItems = computed(() => [
    { label: 'Password policy', value: 'Strong', icon: 'password' },
    { label: 'JWT session expiry', value: this.settings()?.jwtSessionExpiry ?? '2 hours', icon: 'timer' },
    { label: 'Role review', value: 'Due in 12 days', icon: 'fact_check' },
  ]);

  constructor(
    private readonly http: HttpClient,
    private readonly snackBar: MatSnackBar,
    private readonly auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.loadSettings();
  }

  saveSettings(): void {
    this.saving = true;
    this.http.put<AccountSettings>(`${this.apiUrl}/account/settings`, this.toPayload()).subscribe({
      next: settings => {
        this.applySettings(settings);
        this.saving = false;
        this.showMessage('Settings saved');
      },
      error: () => {
        this.saving = false;
        this.showMessage('Unable to save settings');
      },
    });
  }

  signOutAll(): void {
    this.auth.logout();
  }

  private loadSettings(): void {
    this.http.get<AccountSettings>(`${this.apiUrl}/account/settings`).subscribe({
      next: settings => this.applySettings(settings),
      error: () => this.showMessage('Unable to load account settings'),
    });
  }

  private applySettings(settings: AccountSettings): void {
    this.settings.set(settings);
    this.emailAlerts = settings.emailAlerts;
    this.criticalOnly = settings.criticalOnly;
    this.weeklyDigest = settings.weeklyDigest;
    this.browserPush = settings.browserPush;
    this.mfaEnabled = settings.mfaEnabled;
    this.autoAssign = settings.autoAssign;
    this.compactWorkspace = settings.compactWorkspace;
    this.auditExports = settings.auditExports;
  }

  private toPayload(): Omit<AccountSettings, 'jwtSessionExpiry' | 'activeSessions' | 'alertChannels'> {
    return {
      emailAlerts: this.emailAlerts,
      criticalOnly: this.criticalOnly,
      weeklyDigest: this.weeklyDigest,
      browserPush: this.browserPush,
      mfaEnabled: this.mfaEnabled,
      autoAssign: this.autoAssign,
      compactWorkspace: this.compactWorkspace,
      auditExports: this.auditExports,
    };
  }

  private browserName(): string {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Edg/')) {
      return 'Edge on Windows';
    }
    if (userAgent.includes('Chrome/')) {
      return 'Chrome on Windows';
    }
    if (userAgent.includes('Firefox/')) {
      return 'Firefox on Windows';
    }
    return 'Current browser';
  }

  private showMessage(message: string): void {
    this.snackBar.open(message, '×', {
      duration: 2500,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: 'app-snackbar-panel',
    });
  }
}
