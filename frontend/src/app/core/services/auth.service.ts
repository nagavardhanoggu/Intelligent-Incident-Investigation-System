import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, map, tap } from 'rxjs';
import { Permission, ROLE_PERMISSIONS, Role } from '../auth/rbac';

export interface SessionUser {
  id: number;
  fullName: string;
  email: string;
  role: Role;
  roles: Role[];
  permissions: Permission[];
}

interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  user: SessionUser;
}

export interface PasswordResetResponse {
  message: string;
  email?: string;
  expiresInMinutes?: number;
  debugOtp?: string;
}

export interface PasswordResetOtpVerifyResponse {
  message: string;
  resetToken: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly storageKey = 'iiis.session';
  private readonly accessTokenKey = 'iiis.token';
  private readonly refreshTokenKey = 'iiis.refreshToken';
  readonly currentUser = signal<SessionUser | null>(this.loadUser());

  constructor(
    private readonly http: HttpClient,
    private readonly router: Router,
  ) {}

  login(email: string, password: string): Observable<boolean> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, { email, password }).pipe(
      tap(response => {
        localStorage.setItem(this.storageKey, JSON.stringify(response.user));
        localStorage.setItem(this.accessTokenKey, response.accessToken);
        localStorage.setItem(this.refreshTokenKey, response.refreshToken);
        this.currentUser.set(response.user);
      }),
      map(() => true),
    );
  }

  requestPasswordReset(email: string): Observable<PasswordResetResponse> {
    return this.http.post<PasswordResetResponse>(`${this.apiUrl}/auth/forgot-password`, { email });
  }

  verifyPasswordResetOtp(email: string, otp: string): Observable<PasswordResetOtpVerifyResponse> {
    return this.http.post<PasswordResetOtpVerifyResponse>(`${this.apiUrl}/auth/forgot-password/verify-otp`, { email, otp });
  }

  confirmPasswordReset(email: string, otp: string, resetToken: string, newPassword: string, confirmPassword: string): Observable<PasswordResetResponse> {
    return this.http.post<PasswordResetResponse>(`${this.apiUrl}/auth/forgot-password/reset`, {
      email,
      otp,
      resetToken,
      newPassword,
      confirmPassword,
    });
  }

  logout(): void {
    localStorage.removeItem(this.storageKey);
    localStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  isAuthenticated(): boolean {
    return Boolean(this.currentUser() && localStorage.getItem(this.accessTokenKey));
  }

  hasRole(roles: Role[]): boolean {
    const user = this.currentUser();
    return Boolean(user && user.roles.some(role => roles.includes(role)));
  }

  hasAnyPermission(permissions: Permission[]): boolean {
    const user = this.currentUser();
    return Boolean(user && permissions.some(permission => user.permissions.includes(permission)));
  }

  hasAllPermissions(permissions: Permission[]): boolean {
    const user = this.currentUser();
    return Boolean(user && permissions.every(permission => user.permissions.includes(permission)));
  }

  canAccess(roles?: Role[], permissions?: Permission[]): boolean {
    const roleAllowed = !roles?.length || this.hasRole(roles);
    const permissionAllowed = !permissions?.length || this.hasAnyPermission(permissions);
    return roleAllowed && permissionAllowed;
  }

  updateProfile(profile: Pick<SessionUser, 'fullName' | 'email'>): void {
    const user = this.currentUser();
    if (!user) {
      return;
    }

    const updatedUser = { ...user, ...profile };
    localStorage.setItem(this.storageKey, JSON.stringify(updatedUser));
    this.currentUser.set(updatedUser);
  }

  private loadUser(): SessionUser | null {
    if (!localStorage.getItem(this.accessTokenKey)) {
      localStorage.removeItem(this.storageKey);
      localStorage.removeItem(this.refreshTokenKey);
      return null;
    }

    const raw = localStorage.getItem(this.storageKey);
    if (!raw) {
      return null;
    }

    try {
      const parsed = JSON.parse(raw) as SessionUser;
      const roles = parsed.roles?.length ? parsed.roles : [parsed.role];
      const rolePermissions = roles.flatMap(role => ROLE_PERMISSIONS[role] ?? []);
      return {
        ...parsed,
        roles,
        permissions: Array.from(new Set([...(parsed.permissions ?? []), ...rolePermissions])),
      };
    } catch {
      localStorage.removeItem(this.storageKey);
      localStorage.removeItem(this.accessTokenKey);
      localStorage.removeItem(this.refreshTokenKey);
      return null;
    }
  }
}
