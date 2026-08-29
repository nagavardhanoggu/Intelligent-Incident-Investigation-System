import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Permission } from '../auth/rbac';
import { AuthService } from '../services/auth.service';

export const permissionGuard: CanActivateFn = route => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const permissions = route.data['permissions'] as Permission[] | undefined;
  const requireAll = Boolean(route.data['requireAllPermissions']);

  if (!permissions?.length) {
    return true;
  }

  return (
    requireAll
      ? auth.hasAllPermissions(permissions)
      : auth.hasAnyPermission(permissions)
  ) || router.createUrlTree(['/dashboard']);
};
