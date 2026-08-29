import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { permissionGuard } from './core/guards/permission.guard';
import { roleGuard } from './core/guards/role.guard';
import { ShellLayoutComponent } from './layouts/shell-layout/shell-layout.component';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/login/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'forgot-password',
    loadComponent: () => import('./features/forgot-password/forgot-password.component').then(m => m.ForgotPasswordComponent),
  },
  {
    path: '',
    component: ShellLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        canActivate: [permissionGuard],
        data: { permissions: ['dashboard:view'] },
        loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
      },
      {
        path: 'triage',
        canActivate: [permissionGuard],
        data: { permissions: ['triage:view'], pageKey: 'triage' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'incidents',
        canActivate: [permissionGuard],
        data: { permissions: ['incidents:view'] },
        loadComponent: () => import('./features/incidents/incident-list/incident-list.component').then(m => m.IncidentListComponent),
      },
      {
        path: 'incidents/new',
        canActivate: [permissionGuard],
        data: { permissions: ['incidents:create'] },
        loadComponent: () => import('./features/incidents/create-incident/create-incident.component').then(m => m.CreateIncidentComponent),
      },
      {
        path: 'incidents/:id',
        canActivate: [permissionGuard],
        data: { permissions: ['incidents:view_details'] },
        loadComponent: () => import('./features/incidents/incident-details/incident-details.component').then(m => m.IncidentDetailsComponent),
      },
      {
        path: 'investigation',
        canActivate: [permissionGuard],
        data: { permissions: ['incidents:update_assigned', 'incidents:update_any'] },
        loadComponent: () => import('./features/investigation/investigation-landing/investigation-landing.component').then(m => m.InvestigationLandingComponent),
      },
      {
        path: 'investigation/:id',
        canActivate: [permissionGuard],
        data: { permissions: ['incidents:update_assigned', 'incidents:update_any'] },
        loadComponent: () => import('./features/investigation/investigation-workspace/investigation-workspace.component').then(m => m.InvestigationWorkspaceComponent),
      },
      {
        path: 'knowledge-base',
        canActivate: [permissionGuard],
        data: { permissions: ['resolutions:view'] },
        loadComponent: () => import('./features/knowledge-base/knowledge-base.component').then(m => m.KnowledgeBaseComponent),
      },
      {
        path: 'logs',
        canActivate: [permissionGuard],
        data: { permissions: ['logs:view'] },
        loadComponent: () => import('./features/logs/logs.component').then(m => m.LogsComponent),
      },
      {
        path: 'evidence',
        canActivate: [permissionGuard],
        data: { permissions: ['evidence:view'], pageKey: 'evidence' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'metrics',
        canActivate: [permissionGuard],
        data: { permissions: ['metrics:view'] },
        loadComponent: () => import('./features/metrics/metrics.component').then(m => m.MetricsComponent),
      },
      {
        path: 'runbooks',
        canActivate: [permissionGuard],
        data: { permissions: ['runbooks:view'], pageKey: 'runbooks' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'postmortems',
        canActivate: [permissionGuard],
        data: { permissions: ['postmortems:view'], pageKey: 'postmortems' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'service-catalog',
        canActivate: [permissionGuard],
        data: { permissions: ['service_catalog:view'], pageKey: 'service-catalog' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'escalations',
        canActivate: [permissionGuard],
        data: { permissions: ['escalations:view'], pageKey: 'escalations' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'services',
        canActivate: [permissionGuard],
        data: { permissions: ['operations:services:view'] },
        loadComponent: () => import('./features/operations/service-health/service-health.component').then(m => m.ServiceHealthComponent),
      },
      {
        path: 'deployments',
        canActivate: [permissionGuard],
        data: { permissions: ['operations:deployments:view'] },
        loadComponent: () => import('./features/operations/deployments/deployments.component').then(m => m.DeploymentsComponent),
      },
      {
        path: 'sla-monitor',
        canActivate: [permissionGuard],
        data: { permissions: ['operations:sla:view'] },
        loadComponent: () => import('./features/operations/sla-monitor/sla-monitor.component').then(m => m.SlaMonitorComponent),
      },
      {
        path: 'alert-rules',
        canActivate: [permissionGuard],
        data: { permissions: ['operations:alerts:view'] },
        loadComponent: () => import('./features/operations/alert-rules/alert-rules.component').then(m => m.AlertRulesComponent),
      },
      {
        path: 'change-calendar',
        canActivate: [permissionGuard],
        data: { permissions: ['operations:changes:view'] },
        loadComponent: () => import('./features/operations/change-calendar/change-calendar.component').then(m => m.ChangeCalendarComponent),
      },
      {
        path: 'on-call',
        canActivate: [permissionGuard],
        data: { permissions: ['operations:oncall:view'] },
        loadComponent: () => import('./features/operations/on-call/on-call.component').then(m => m.OnCallComponent),
      },
      {
        path: 'root-cause',
        canActivate: [permissionGuard],
        data: { permissions: ['operations:rootcause:view'] },
        loadComponent: () => import('./features/operations/root-cause/root-cause.component').then(m => m.RootCauseComponent),
      },
      {
        path: 'reports',
        canActivate: [permissionGuard],
        data: { permissions: ['reports:view'] },
        loadComponent: () => import('./features/reports/reports.component').then(m => m.ReportsComponent),
      },
      {
        path: 'model-monitoring',
        canActivate: [permissionGuard],
        data: { permissions: ['model_monitoring:view'], pageKey: 'model-monitoring' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'ml-training',
        canActivate: [permissionGuard],
        data: { permissions: ['predictions:run'] },
        loadComponent: () => import('./features/ml-training/ml-training.component').then(m => m.MlTrainingComponent),
      },
      {
        path: 'admin/users',
        canActivate: [roleGuard],
        data: { roles: ['ADMIN'] },
        loadComponent: () => import('./features/admin/user-management/user-management.component').then(m => m.UserManagementComponent),
      },
      {
        path: 'data-sources',
        canActivate: [permissionGuard],
        data: { permissions: ['data_sources:view'], pageKey: 'data-sources' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'audit-trail',
        canActivate: [permissionGuard],
        data: { permissions: ['audit_trail:view'], pageKey: 'audit-trail' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'settings',
        canActivate: [permissionGuard],
        data: { permissions: ['settings:view'], pageKey: 'settings' },
        loadComponent: () => import('./features/feature-pages/feature-page.component').then(m => m.FeaturePageComponent),
      },
      {
        path: 'account/profile',
        loadComponent: () => import('./features/account/profile/profile.component').then(m => m.ProfileComponent),
      },
      {
        path: 'account/access-role',
        loadComponent: () => import('./features/account/access-role/access-role.component').then(m => m.AccessRoleComponent),
      },
      {
        path: 'account/settings',
        loadComponent: () => import('./features/account/account-settings/account-settings.component').then(m => m.AccountSettingsComponent),
      },
      {
        path: 'notifications',
        loadComponent: () => import('./features/notifications/notifications.component').then(m => m.NotificationsComponent),
      },
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
