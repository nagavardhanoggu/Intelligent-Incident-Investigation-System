export type Role = 'ADMIN' | 'INVESTIGATOR' | 'VIEWER';

export type Permission =
  | 'users:create'
  | 'users:update'
  | 'users:delete'
  | 'users:assign_roles'
  | 'users:view'
  | 'incidents:create'
  | 'incidents:view'
  | 'incidents:view_details'
  | 'incidents:update_any'
  | 'incidents:update_assigned'
  | 'incidents:assign'
  | 'incidents:close'
  | 'incidents:delete'
  | 'logs:upload'
  | 'logs:view'
  | 'logs:search'
  | 'metrics:create'
  | 'metrics:view'
  | 'predictions:run'
  | 'predictions:view'
  | 'resolutions:create'
  | 'resolutions:view'
  | 'resolutions:manage'
  | 'reports:view'
  | 'reports:export'
  | 'reports:manage'
  | 'operations:services:view'
  | 'operations:deployments:view'
  | 'operations:changes:view'
  | 'operations:sla:view'
  | 'operations:alerts:view'
  | 'operations:oncall:view'
  | 'operations:rootcause:view'
  | 'triage:view'
  | 'evidence:view'
  | 'runbooks:view'
  | 'postmortems:view'
  | 'service_catalog:view'
  | 'escalations:view'
  | 'model_monitoring:view'
  | 'data_sources:view'
  | 'audit_trail:view'
  | 'settings:view'
  | 'dashboard:view'
  | 'dashboard:admin'
  | 'dashboard:investigator'
  | 'dashboard:viewer';

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  ADMIN: [
    'users:create', 'users:update', 'users:delete', 'users:assign_roles', 'users:view',
    'incidents:create', 'incidents:view', 'incidents:view_details', 'incidents:update_any',
    'incidents:update_assigned', 'incidents:assign', 'incidents:close', 'incidents:delete',
    'logs:upload', 'logs:view', 'logs:search',
    'metrics:create', 'metrics:view',
    'predictions:run', 'predictions:view',
    'resolutions:create', 'resolutions:view', 'resolutions:manage',
    'reports:view', 'reports:export', 'reports:manage',
    'operations:services:view', 'operations:deployments:view', 'operations:changes:view',
    'operations:sla:view', 'operations:alerts:view', 'operations:oncall:view',
    'operations:rootcause:view',
    'triage:view', 'evidence:view', 'runbooks:view', 'postmortems:view',
    'service_catalog:view', 'escalations:view', 'model_monitoring:view',
    'data_sources:view', 'audit_trail:view', 'settings:view',
    'dashboard:view', 'dashboard:admin', 'dashboard:investigator', 'dashboard:viewer',
  ],
  INVESTIGATOR: [
    'dashboard:view', 'dashboard:investigator',
    'incidents:create', 'incidents:view', 'incidents:view_details', 'incidents:update_assigned', 'incidents:close',
    'logs:upload', 'logs:view', 'logs:search',
    'metrics:create', 'metrics:view',
    'predictions:run', 'predictions:view',
    'resolutions:create', 'resolutions:view',
    'reports:view',
    'operations:services:view', 'operations:deployments:view', 'operations:changes:view',
    'operations:sla:view', 'operations:alerts:view', 'operations:oncall:view',
    'operations:rootcause:view',
    'triage:view', 'evidence:view', 'runbooks:view', 'postmortems:view',
    'service_catalog:view', 'escalations:view', 'model_monitoring:view',
  ],
  VIEWER: [
    'dashboard:view', 'dashboard:viewer',
    'incidents:view', 'incidents:view_details',
    'predictions:view',
    'resolutions:view',
    'reports:view',
    'operations:rootcause:view',
    'evidence:view', 'runbooks:view', 'postmortems:view', 'service_catalog:view',
  ],
};
