import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, HostListener, OnInit, ViewChild, computed, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Permission, Role } from '../../core/auth/rbac';
import { AuthService } from '../../core/services/auth.service';
import { ThemeService } from '../../core/services/theme.service';
import { NotificationService } from '../../services/notification.service';

interface NavItem {
  label: string;
  route: string;
  icon: string;
  roles?: Role[];
  permissions?: Permission[];
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

interface SearchResult {
  label: string;
  detail: string;
  icon: string;
  route: string;
  keywords: string;
  roles?: Role[];
  permissions?: Permission[];
}

interface AccountMenuLink extends NavItem {
  detail: string;
}

interface DashboardSummary {
  totalIncidents: number;
  openIncidents: number;
  closedIncidents: number;
  criticalIncidents: number;
  slaCompliance: number;
}

@Component({
  selector: 'app-shell-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, MatBadgeModule, MatButtonModule, MatIconModule, MatMenuModule, MatSidenavModule, MatToolbarModule],
  templateUrl: './shell-layout.component.html',
  styleUrl: './shell-layout.component.scss',
})
export class ShellLayoutComponent implements OnInit {
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  readonly theme = inject(ThemeService);
  private readonly notificationService = inject(NotificationService);
  @ViewChild('globalSearchInput') private searchInput?: ElementRef<HTMLInputElement>;
  readonly user = computed(() => this.auth.currentUser());
  readonly permissionCount = computed(() => this.user()?.permissions.length ?? 0);
  readonly searchQuery = signal('');
  readonly searchFocused = signal(false);
  readonly navGroups: NavGroup[] = [
    {
      label: 'Overview',
      items: [
        { label: 'Dashboard', route: '/dashboard', icon: 'dashboard', permissions: ['dashboard:view'] },
        { label: 'Triage Board', route: '/triage', icon: 'fact_check', permissions: ['triage:view'] },
        { label: 'Incidents', route: '/incidents', icon: 'report_problem', permissions: ['incidents:view'] },
      ],
    },
    {
      label: 'Investigation',
      items: [
        { label: 'Workspace', route: '/investigation', icon: 'manage_search', permissions: ['incidents:update_assigned', 'incidents:update_any'] },
        { label: 'Evidence Center', route: '/evidence', icon: 'folder_copy', permissions: ['evidence:view'] },
        { label: 'Logs', route: '/logs', icon: 'article', permissions: ['logs:view'] },
        { label: 'Metrics', route: '/metrics', icon: 'monitoring', permissions: ['metrics:view'] },
        { label: 'ML Training', route: '/ml-training', icon: 'account_tree', permissions: ['predictions:run'] },
      ],
    },
    {
      label: 'Operations',
      items: [
        { label: 'Service Catalog', route: '/service-catalog', icon: 'apps', permissions: ['service_catalog:view'] },
        { label: 'Escalations', route: '/escalations', icon: 'outbound', permissions: ['escalations:view'] },
        { label: 'Services', route: '/services', icon: 'dns', permissions: ['operations:services:view'] },
        { label: 'Deployments', route: '/deployments', icon: 'rocket_launch', permissions: ['operations:deployments:view'] },
        { label: 'Change Calendar', route: '/change-calendar', icon: 'event', permissions: ['operations:changes:view'] },
        { label: 'SLA Monitor', route: '/sla-monitor', icon: 'timer', permissions: ['operations:sla:view'] },
        { label: 'Alert Rules', route: '/alert-rules', icon: 'notifications_active', permissions: ['operations:alerts:view'] },
        { label: 'On-Call', route: '/on-call', icon: 'support_agent', permissions: ['operations:oncall:view'] },
        { label: 'Root Cause', route: '/root-cause', icon: 'device_hub', permissions: ['operations:rootcause:view'] },
      ],
    },
    {
      label: 'Knowledge',
      items: [
        { label: 'Knowledge Base', route: '/knowledge-base', icon: 'library_books', permissions: ['resolutions:view'] },
        { label: 'Runbooks', route: '/runbooks', icon: 'menu_book', permissions: ['runbooks:view'] },
        { label: 'Postmortems', route: '/postmortems', icon: 'history_edu', permissions: ['postmortems:view'] },
      ],
    },
    {
      label: 'Intelligence',
      items: [
        { label: 'Reports', route: '/reports', icon: 'bar_chart', permissions: ['reports:view'] },
        { label: 'Model Monitoring', route: '/model-monitoring', icon: 'model_training', permissions: ['model_monitoring:view'] },
      ],
    },
    {
      label: 'Admin',
      items: [
        { label: 'Users', route: '/admin/users', icon: 'admin_panel_settings', roles: ['ADMIN'], permissions: ['users:view'] },
        { label: 'Data Sources', route: '/data-sources', icon: 'storage', roles: ['ADMIN'], permissions: ['data_sources:view'] },
        { label: 'Audit Trail', route: '/audit-trail', icon: 'policy', roles: ['ADMIN'], permissions: ['audit_trail:view'] },
        { label: 'System Settings', route: '/settings', icon: 'settings', roles: ['ADMIN'], permissions: ['settings:view'] },
      ],
    },
    {
      label: 'Account',
      items: [
        { label: 'Access Role', route: '/account/access-role', icon: 'shield' },
        { label: 'Account Settings', route: '/account/settings', icon: 'manage_accounts' },
      ],
    },
  ];
  readonly accountMenuLinks: AccountMenuLink[] = [
    { label: 'Profile', detail: 'Identity and activity', route: '/account/profile', icon: 'person' },
  ];
  readonly visibleNavGroups = computed(() =>
    this.navGroups
      .map(group => ({
        ...group,
        items: group.items.filter(item => this.auth.canAccess(item.roles, item.permissions)),
      }))
      .filter(group => group.items.length > 0),
  );
  readonly visibleAccountMenuLinks = computed(() => this.accountMenuLinks.filter(item => this.auth.canAccess(item.roles, item.permissions)));

  readonly alerts = this.notificationService.notifications;
  readonly unreadAlerts = this.notificationService.unreadCount;
  readonly unreadAlertItems = computed(() => this.alerts().filter(alert => !alert.read));
  readonly dashboardSummary = signal<DashboardSummary | null>(null);
  readonly themeIcon = computed(() => this.theme.isDark() ? 'light_mode' : 'dark_mode');
  readonly themeToggleLabel = computed(() => this.theme.isDark() ? 'Switch to light theme' : 'Switch to dark theme');
  readonly searchResults = computed(() => {
    const query = this.searchQuery().trim().toLowerCase();

    if (!query) {
      return this.visibleSearchIndex().slice(0, 5);
    }

    return this.visibleSearchIndex()
      .filter(item => `${item.label} ${item.detail} ${item.keywords}`.toLowerCase().includes(query))
      .slice(0, 6);
  });

  readonly showSearchResults = computed(() => this.searchFocused() && (this.searchResults().length > 0 || this.searchQuery().trim().length > 0));
  readonly hasSearchResults = computed(() => this.searchResults().length > 0);

  private readonly searchIndex: SearchResult[] = [
    { label: 'Dashboard', detail: 'Incident trends, SLA health, and root-cause charts', icon: 'dashboard', route: '/dashboard', keywords: 'home metrics summary critical open closed', permissions: ['dashboard:view'] },
    { label: 'Triage Board', detail: 'Prioritize intake, SLA risk, and ownership', icon: 'fact_check', route: '/triage', keywords: 'triage intake priority sla owner p1 p2', permissions: ['triage:view'] },
    { label: 'Incidents', detail: 'Search, filter, assign, and close incidents', icon: 'report_problem', route: '/incidents', keywords: 'incident list priority status assigned', permissions: ['incidents:view'] },
    { label: 'Create Incident', detail: 'Capture a new production incident', icon: 'add_alert', route: '/incidents/new', keywords: 'new create incident ticket', permissions: ['incidents:create'] },
    { label: 'Checkout latency spike', detail: 'INC-2026-000101 · Critical investigation', icon: 'manage_search', route: '/investigation/101', keywords: 'checkout api latency critical database timeout', permissions: ['incidents:update_assigned', 'incidents:update_any'] },
    { label: 'Evidence Center', detail: 'Logs, metrics, predictions, and timeline evidence', icon: 'folder_copy', route: '/evidence', keywords: 'evidence logs metrics prediction timeline artifacts', permissions: ['evidence:view'] },
    { label: 'Logs', detail: 'Upload and search incident-specific logs', icon: 'article', route: '/logs', keywords: 'log txt csv upload search', permissions: ['logs:view'] },
    { label: 'Metrics', detail: 'CPU, memory, response time, errors, DB connections', icon: 'monitoring', route: '/metrics', keywords: 'cpu memory disk response error database connection', permissions: ['metrics:view'] },
    { label: 'Runbooks', detail: 'Recovery procedures for common root causes', icon: 'menu_book', route: '/runbooks', keywords: 'runbook recovery database deployment memory dns actions', permissions: ['runbooks:view'] },
    { label: 'Postmortems', detail: 'Closed incident reviews and prevention commitments', icon: 'history_edu', route: '/postmortems', keywords: 'postmortem review root cause prevention closed incident', permissions: ['postmortems:view'] },
    { label: 'Service Catalog', detail: 'Service owners, dependencies, and criticality', icon: 'apps', route: '/service-catalog', keywords: 'service catalog owner dependency criticality', permissions: ['service_catalog:view'] },
    { label: 'Escalations', detail: 'Escalation ownership, handoff, and policy status', icon: 'outbound', route: '/escalations', keywords: 'escalation handoff commander bridge policy ack', permissions: ['escalations:view'] },
    { label: 'Services', detail: 'Service health, ownership, and live risk state', icon: 'dns', route: '/services', keywords: 'service health dependency uptime owner operations', permissions: ['operations:services:view'] },
    { label: 'Deployments', detail: 'Recent releases and incident-linked changes', icon: 'rocket_launch', route: '/deployments', keywords: 'deployment release rollback change ci cd', permissions: ['operations:deployments:view'] },
    { label: 'Change Calendar', detail: 'Scheduled changes and production freeze windows', icon: 'event', route: '/change-calendar', keywords: 'change calendar release schedule freeze deployment', permissions: ['operations:changes:view'] },
    { label: 'SLA Monitor', detail: 'SLA targets, breach risk, and response windows', icon: 'timer', route: '/sla-monitor', keywords: 'sla breach target mttr response error budget', permissions: ['operations:sla:view'] },
    { label: 'Alert Rules', detail: 'Operational alert policies and routing rules', icon: 'notifications_active', route: '/alert-rules', keywords: 'alert rules notification threshold escalation', permissions: ['operations:alerts:view'] },
    { label: 'On-Call', detail: 'Escalation ownership and current responder coverage', icon: 'support_agent', route: '/on-call', keywords: 'on call responder escalation ownership schedule', permissions: ['operations:oncall:view'] },
    { label: 'Root Cause', detail: 'Root cause patterns, confidence, and recurring failure modes', icon: 'device_hub', route: '/root-cause', keywords: 'root cause database deployment network memory application', permissions: ['operations:rootcause:view'] },
    { label: 'Knowledge Base', detail: 'Resolution articles and reusable playbooks', icon: 'library_books', route: '/knowledge-base', keywords: 'root cause resolution prevention database memory network deployment', permissions: ['resolutions:view'] },
    { label: 'ML Training', detail: 'Decision Tree model and dataset preprocessing', icon: 'account_tree', route: '/ml-training', keywords: 'machine learning kaggle decision tree classifier prediction', permissions: ['predictions:run'] },
    { label: 'Reports', detail: 'Monthly MTTR and SLA reports', icon: 'bar_chart', route: '/reports', keywords: 'monthly trend report mttr sla', permissions: ['reports:view'] },
    { label: 'Model Monitoring', detail: 'Accuracy, confidence, artifact size, and drift', icon: 'model_training', route: '/model-monitoring', keywords: 'model monitoring accuracy confidence drift classifier artifact', permissions: ['model_monitoring:view'] },
    { label: 'Users', detail: 'User access and role management', icon: 'admin_panel_settings', route: '/admin/users', keywords: 'admin create edit delete users role', roles: ['ADMIN'], permissions: ['users:view'] },
    { label: 'Data Sources', detail: 'Log feeds, metric sources, CSV imports, and sync health', icon: 'storage', route: '/data-sources', keywords: 'data sources import csv logs metrics sync admin', roles: ['ADMIN'], permissions: ['data_sources:view'] },
    { label: 'Audit Trail', detail: 'System access, updates, imports, exports, and denials', icon: 'policy', route: '/audit-trail', keywords: 'audit trail logs access role export import denied admin', roles: ['ADMIN'], permissions: ['audit_trail:view'] },
    { label: 'System Settings', detail: 'SLA thresholds, alert defaults, and platform controls', icon: 'settings', route: '/settings', keywords: 'settings configuration sla thresholds alerts admin', roles: ['ADMIN'], permissions: ['settings:view'] },
  ];
  private readonly visibleSearchIndex = computed(() => this.searchIndex.filter(item => this.auth.canAccess(item.roles, item.permissions)));

  ngOnInit(): void {
    this.notificationService.load();
    if (this.auth.hasAnyPermission(['dashboard:view'])) {
      this.loadDashboardSummary();
    }
  }

  @HostListener('document:keydown.control.k', ['$event'])
  focusSearch(event: Event): void {
    event.preventDefault();
    this.searchInput?.nativeElement.focus();
    this.searchFocused.set(true);
  }

  updateSearch(event: Event): void {
    this.searchQuery.set((event.target as HTMLInputElement).value);
    this.searchFocused.set(true);
  }

  clearSearch(event?: Event): void {
    event?.preventDefault();
    this.searchQuery.set('');
    this.searchFocused.set(true);
    this.searchInput?.nativeElement.focus();
  }

  closeSearchResults(): void {
    window.setTimeout(() => this.searchFocused.set(false), 150);
  }

  selectSearchResult(result: SearchResult): void {
    this.searchQuery.set('');
    this.searchFocused.set(false);
    this.router.navigate([result.route]);
  }

  submitSearch(event: Event): void {
    event.preventDefault();
    const [firstResult] = this.searchResults();
    if (firstResult) {
      this.selectSearchResult(firstResult);
    }
  }

  markAllAlertsRead(event: MouseEvent): void {
    event.stopPropagation();
    this.notificationService.markAllRead();
  }

  markAlertRead(alertId: number): void {
    this.notificationService.markRead(alertId);
  }

  logout(): void {
    this.auth.logout();
  }

  toggleTheme(): void {
    this.theme.toggle();
  }

  private loadDashboardSummary(): void {
    this.http.get<DashboardSummary>(`${this.apiUrl}/dashboard/summary`).subscribe({
      next: summary => this.dashboardSummary.set(summary),
    });
  }
}
