import { HttpClient } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../core/services/auth.service';
import { ThemeService } from '../../core/services/theme.service';

interface LoginOperationsSummary {
  criticalIncidents: number;
  openIncidents: number;
  slaCompliance: number;
}

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink, MatButtonModule, MatCardModule, MatCheckboxModule, MatFormFieldModule, MatIconModule, MatInputModule, MatProgressSpinnerModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  readonly theme = inject(ThemeService);
  private readonly minimumLoadingMs = 5000;

  readonly form = this.fb.nonNullable.group({
    email: ['admin@example.com', [Validators.required, Validators.email]],
    password: ['password', Validators.required],
    rememberMe: [true],
  });
  readonly loginError = signal('');
  readonly loading = signal(false);
  readonly hidePassword = signal(true);
  readonly selectedRole = signal('Admin');
  readonly operationsSummary = signal<LoginOperationsSummary | null>(null);
  readonly themeIcon = computed(() => this.theme.isDark() ? 'light_mode' : 'dark_mode');
  readonly themeToggleLabel = computed(() => this.theme.isDark() ? 'Switch to light theme' : 'Switch to dark theme');
  readonly demoAccounts = [
    { role: 'Admin', email: 'admin@example.com', password: 'password', icon: 'admin_panel_settings' },
    { role: 'Investigator', email: 'investigator@example.com', password: 'password', icon: 'manage_search' },
    { role: 'Viewer', email: 'viewer@example.com', password: 'password', icon: 'visibility' },
  ];
  readonly trustSignals = [
    { icon: 'verified_user', label: 'RBAC enforced', value: '3 roles' },
    { icon: 'psychology', label: 'ML analysis', value: 'Decision Tree' },
    { icon: 'monitoring', label: 'Signals tracked', value: 'Logs + Metrics' },
  ];
  readonly operationSignals = computed(() => {
    const summary = this.operationsSummary();

    return [
      { icon: 'report_problem', label: `${summary?.criticalIncidents ?? '-'} Critical` },
      { icon: 'pending_actions', label: `${summary?.openIncidents ?? '-'} Open` },
      { icon: 'verified', label: `${summary?.slaCompliance ?? '-'}% SLA` },
    ];
  });

  constructor() {
    this.http.get<LoginOperationsSummary>(`${this.apiUrl}/auth/operations-summary`).subscribe({
      next: summary => this.operationsSummary.set(summary),
      error: () => this.operationsSummary.set(null),
    });
  }

  selectAccount(account: (typeof this.demoAccounts)[number]): void {
    this.selectedRole.set(account.role);
    this.loginError.set('');
    this.form.setValue({
      email: account.email,
      password: account.password,
      rememberMe: this.form.controls.rememberMe.value,
    });
  }

  toggleTheme(): void {
    this.theme.toggle();
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { email, password } = this.form.getRawValue();
    const startedAt = Date.now();
    this.loginError.set('');
    this.loading.set(true);
    this.auth.login(email, password).subscribe({
      next: () => {
        this.finishLoading(startedAt, () => this.router.navigate(['/dashboard']));
      },
      error: () => {
        this.finishLoading(startedAt, () => this.loginError.set('Invalid email or password.'));
      },
    });
  }

  private finishLoading(startedAt: number, callback: () => void): void {
    const remainingMs = Math.max(this.minimumLoadingMs - (Date.now() - startedAt), 0);
    window.setTimeout(() => {
      callback();
      this.loading.set(false);
    }, remainingMs);
  }
}
