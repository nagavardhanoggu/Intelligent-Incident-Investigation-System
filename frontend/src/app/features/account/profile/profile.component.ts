import { HttpClient } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../../core/services/auth.service';
import { ChangePasswordDialogComponent, ChangePasswordValue } from './change-password-dialog.component';
import { EditProfileDialogComponent, EditProfileValue } from './edit-profile-dialog.component';

type ProfileRole = 'ADMIN' | 'INVESTIGATOR' | 'VIEWER';

interface ProfileDetail {
  label: string;
  value: string;
  icon: string;
}

interface ProfileStat {
  label: string;
  value: string;
}

interface ProfileActivity {
  title: string;
  time: string;
  icon: string;
}

interface AccountProfile {
  user: {
    id: number;
    fullName: string;
    email: string;
    role: ProfileRole;
    status: 'ACTIVE' | 'INACTIVE';
    roles: ProfileRole[];
    permissions: string[];
  };
  details: ProfileDetail[];
  stats: ProfileStat[];
  activity: ProfileActivity[];
}

@Component({
  selector: 'app-profile',
  imports: [MatButtonModule, MatCardModule, MatChipsModule, MatDialogModule, MatIconModule, MatSnackBarModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss',
})
export class ProfileComponent implements OnInit {
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly auth = inject(AuthService);
  private readonly dialog = inject(MatDialog);
  private readonly http = inject(HttpClient);
  private readonly snackBar = inject(MatSnackBar);

  readonly profile = signal<AccountProfile | null>(null);
  readonly user = computed(() => this.profile()?.user ?? this.auth.currentUser());
  readonly details = computed(() => this.profile()?.details ?? []);
  readonly stats = computed(() => this.profile()?.stats ?? []);
  readonly activity = computed(() => this.profile()?.activity ?? []);

  ngOnInit(): void {
    this.loadProfile();
  }

  editProfile(): void {
    const user = this.user();
    if (!user) {
      return;
    }

    const dialogRef = this.dialog.open(EditProfileDialogComponent, {
      width: '520px',
      maxWidth: 'calc(100vw - 32px)',
      panelClass: 'edit-profile-dialog-panel',
      backdropClass: 'app-dialog-backdrop',
      data: {
        fullName: user.fullName,
        email: user.email,
      },
    });

    dialogRef.afterClosed().subscribe((result?: EditProfileValue) => {
      if (!result) {
        return;
      }

      this.http.put<AccountProfile>(`${this.apiUrl}/account/profile`, result).subscribe({
        next: profile => {
          this.profile.set(profile);
          this.auth.updateProfile({ fullName: profile.user.fullName, email: profile.user.email });
          this.showMessage('Profile updated successfully');
        },
        error: error => this.showMessage(error?.error?.detail ?? 'Unable to update profile'),
      });
    });
  }

  changePassword(): void {
    const dialogRef = this.dialog.open(ChangePasswordDialogComponent, {
      width: '520px',
      maxWidth: 'calc(100vw - 32px)',
      panelClass: 'edit-profile-dialog-panel',
      backdropClass: 'app-dialog-backdrop',
    });

    dialogRef.afterClosed().subscribe((result?: ChangePasswordValue) => {
      if (!result) {
        return;
      }

      this.http.put(`${this.apiUrl}/account/password`, result).subscribe({
        next: () => this.showMessage('Password changed successfully'),
        error: error => this.showMessage(error?.error?.detail ?? 'Unable to change password'),
      });
    });
  }

  formatActivityTime(value: string): string {
    const date = new Date(value);
    const minutes = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000));
    if (minutes < 1) {
      return 'Just now';
    }
    if (minutes < 60) {
      return `${minutes} min ago`;
    }

    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
      return `${hours} hr ago`;
    }
    return date.toLocaleDateString();
  }

  private loadProfile(): void {
    this.http.get<AccountProfile>(`${this.apiUrl}/account/profile`).subscribe({
      next: profile => this.profile.set(profile),
      error: () => this.showMessage('Unable to load profile data'),
    });
  }

  private showMessage(message: string): void {
    this.snackBar.open(message, '×', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: 'app-snackbar-panel',
    });
  }
}
