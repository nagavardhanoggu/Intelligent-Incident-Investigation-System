import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Role } from '../auth/rbac';
import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = route => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const roles = route.data['roles'] as Role[];
  return auth.hasRole(roles) || router.createUrlTree(['/dashboard']);
};
