import { Component, Inject, computed } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { UserRow } from './user-management.component';

type Role = 'ADMIN' | 'INVESTIGATOR' | 'VIEWER';
type Status = 'Active' | 'Inactive';

interface UserFormValue {
  name: string;
  email: string;
  password: string;
  role: Role;
  status: Status;
}

export interface UserAccessDialogData {
  mode: 'create' | 'edit';
  user?: UserRow;
  roles?: Role[];
}

@Component({
  selector: 'app-user-access-dialog',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
  ],
  templateUrl: './user-access-dialog.component.html',
  styleUrl: './user-access-dialog.component.scss',
})
export class UserAccessDialogComponent {
  readonly statuses = ['Active', 'Inactive'] as const;
  readonly showPassword = computed(() => this.data.mode === 'create');
  readonly form;

  constructor(
    private readonly dialogRef: MatDialogRef<UserAccessDialogComponent, UserFormValue>,
    @Inject(MAT_DIALOG_DATA) readonly data: UserAccessDialogData,
  ) {
    this.form = new FormBuilder().nonNullable.group({
      name: [data.user?.name ?? '', [Validators.required, Validators.minLength(3)]],
      email: [data.user?.email ?? '', [Validators.required, Validators.email]],
      password: ['', data.mode === 'create' ? [Validators.required, Validators.minLength(8)] : []],
      role: [data.user?.role ?? 'INVESTIGATOR', Validators.required],
      status: [data.user?.status ?? 'Active', Validators.required],
    });
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.dialogRef.close(this.form.getRawValue());
  }
}
