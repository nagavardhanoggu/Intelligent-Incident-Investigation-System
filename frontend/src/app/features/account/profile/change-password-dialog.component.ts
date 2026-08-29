import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

export interface ChangePasswordValue {
  currentPassword: string;
  newPassword: string;
}

@Component({
  selector: 'app-change-password-dialog',
  imports: [ReactiveFormsModule, MatButtonModule, MatDialogModule, MatFormFieldModule, MatIconModule, MatInputModule],
  templateUrl: './change-password-dialog.component.html',
  styleUrl: './edit-profile-dialog.component.scss',
})
export class ChangePasswordDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly dialogRef = inject(MatDialogRef<ChangePasswordDialogComponent, ChangePasswordValue>);

  readonly hideCurrentPassword = signal(true);
  readonly hideNewPassword = signal(true);
  readonly hideConfirmPassword = signal(true);
  readonly form = this.fb.nonNullable.group({
    currentPassword: ['', Validators.required],
    newPassword: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required, Validators.minLength(8)]],
  });
  readonly passwordMismatch = computed(() => {
    const { newPassword, confirmPassword } = this.form.getRawValue();
    return Boolean(confirmPassword && newPassword !== confirmPassword);
  });

  close(): void {
    this.dialogRef.close();
  }

  save(): void {
    if (this.form.invalid || this.passwordMismatch()) {
      this.form.markAllAsTouched();
      return;
    }

    const { currentPassword, newPassword } = this.form.getRawValue();
    this.dialogRef.close({ currentPassword, newPassword });
  }
}
