import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { catchError, forkJoin, of } from 'rxjs';
import { Role } from '../../../core/auth/rbac';
import { AuthService } from '../../../core/services/auth.service';
import { UserAccessDialogComponent, UserAccessDialogData } from './user-access-dialog.component';

export interface UserRow {
  id: number;
  name: string;
  email: string;
  role: Role;
  status: 'Active' | 'Inactive';
}

interface ApiUser {
  id: number;
  fullName: string;
  email: string;
  role: Role;
  status: 'ACTIVE' | 'INACTIVE';
}

interface ApiRole {
  id: number;
  name: Role;
}

interface ImportUserRow {
  name: string;
  email: string;
  password: string;
  role: Role;
  status: 'Active' | 'Inactive';
}

@Component({
  selector: 'app-user-management',
  imports: [
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatDialogModule,
    MatIconModule,
    MatSnackBarModule,
    MatTableModule,
  ],
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.scss',
})
export class UserManagementComponent {
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  readonly columns = ['name', 'email', 'role', 'status', 'actions'];
  users: UserRow[] = [];
  roles: Role[] = [];

  constructor(
    private readonly dialog: MatDialog,
    private readonly http: HttpClient,
    private readonly auth: AuthService,
    private readonly snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadUsers();
    this.loadRoles();
  }

  get activeUsers(): number {
    return this.users.filter(user => user.status === 'Active').length;
  }

  get adminUsers(): number {
    return this.users.filter(user => user.role === 'ADMIN').length;
  }

  openCreateDialog(): void {
    this.openDialog({ mode: 'create' });
  }

  editUser(user: UserRow): void {
    this.openDialog({ mode: 'edit', user });
  }

  deleteUser(user: UserRow): void {
    this.http.delete(`${this.apiUrl}/users/${user.id}`).subscribe(() => {
      this.users = this.users.filter(item => item.id !== user.id);
    });
  }

  exportUsers(): void {
    const rows = [
      ['name', 'email', 'role', 'status'],
      ...this.users.map(user => [user.name, user.email, user.role, user.status]),
    ];
    const csv = rows.map(row => row.map(value => this.csvEscape(value)).join(',')).join('\r\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = `users-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  importUsers(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      try {
        const rows = this.parseImportCsv(String(reader.result ?? ''));
        if (!rows.length) {
          this.showMessage('No valid users found in the CSV file.');
          return;
        }

        const requests = rows.map(row =>
          this.http.post<ApiUser>(`${this.apiUrl}/users`, this.toCreatePayload(row)).pipe(catchError(() => of(null))),
        );

        forkJoin(requests).subscribe(results => {
          const imported = results.filter((user): user is ApiUser => Boolean(user));
          if (imported.length) {
            this.users = [...imported.map(user => this.toRow(user)), ...this.users];
          }
          this.showMessage(`${imported.length} of ${rows.length} users imported.`);
        });
      } catch (error) {
        this.showMessage(error instanceof Error ? error.message : 'Unable to import users.');
      } finally {
        input.value = '';
      }
    };
    reader.readAsText(file);
  }

  canCreateUser(): boolean {
    return this.auth.hasAnyPermission(['users:create']);
  }

  canUpdateUser(): boolean {
    return this.auth.hasAnyPermission(['users:update']);
  }

  canDeleteUser(): boolean {
    return this.auth.hasAnyPermission(['users:delete']);
  }

  private openDialog(data: UserAccessDialogData): void {
    const dialogRef = this.dialog.open(UserAccessDialogComponent, {
      width: '650px',
      maxWidth: 'calc(100vw - 32px)',
      panelClass: 'user-access-dialog-panel',
      backdropClass: 'app-dialog-backdrop',
      data: { ...data, roles: this.roles },
    });

    dialogRef.afterClosed().subscribe((result: (Omit<UserRow, 'id'> & { password?: string }) | undefined) => {
      if (!result) {
        return;
      }

      if (data.mode === 'edit' && data.user) {
        this.http.put<ApiUser>(`${this.apiUrl}/users/${data.user.id}`, this.toUpdatePayload(result)).subscribe(user => {
          this.users = this.users.map(item => item.id === data.user?.id ? this.toRow(user) : item);
        });
        return;
      }

      this.http.post<ApiUser>(`${this.apiUrl}/users`, this.toCreatePayload(result)).subscribe(user => {
        this.users = [this.toRow(user), ...this.users];
      });
    });
  }

  private loadUsers(): void {
    this.http.get<ApiUser[]>(`${this.apiUrl}/users`).subscribe(users => {
      this.users = users.map(user => this.toRow(user));
    });
  }

  private loadRoles(): void {
    this.http.get<ApiRole[]>(`${this.apiUrl}/users/roles`).subscribe(roles => {
      this.roles = roles.map(role => role.name);
    });
  }

  private toRow(user: ApiUser): UserRow {
    return {
      id: user.id,
      name: user.fullName,
      email: user.email,
      role: user.role,
      status: user.status === 'ACTIVE' ? 'Active' : 'Inactive',
    };
  }

  private toCreatePayload(user: Omit<UserRow, 'id'> & { password?: string }): object {
    return {
      fullName: user.name,
      email: user.email,
      password: user.password,
      role: user.role,
      status: user.status.toUpperCase(),
    };
  }

  private toUpdatePayload(user: Omit<UserRow, 'id'>): object {
    return {
      fullName: user.name,
      email: user.email,
      role: user.role,
      status: user.status.toUpperCase(),
    };
  }

  private csvEscape(value: string | number): string {
    const text = String(value ?? '');
    return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  }

  private parseImportCsv(csv: string): ImportUserRow[] {
    const table = this.parseCsvRows(csv).filter(row => row.some(cell => cell.trim()));
    if (table.length < 2) {
      return [];
    }

    const headers = table[0].map(header => header.trim().toLowerCase());
    const indexOf = (...names: string[]) => names.map(name => headers.indexOf(name)).find(index => index >= 0) ?? -1;
    const nameIndex = indexOf('name', 'fullname', 'full name');
    const emailIndex = indexOf('email');
    const passwordIndex = indexOf('password');
    const roleIndex = indexOf('role');
    const statusIndex = indexOf('status');
    const validRoles = this.roles.length ? this.roles : (['ADMIN', 'INVESTIGATOR', 'VIEWER'] as Role[]);

    if (nameIndex < 0 || emailIndex < 0 || passwordIndex < 0 || roleIndex < 0 || statusIndex < 0) {
      throw new Error('Import CSV must include name, email, password, role, and status columns.');
    }

    return table.slice(1).map(row => {
      const role = row[roleIndex]?.trim().toUpperCase() as Role;
      const rawStatus = row[statusIndex]?.trim().toUpperCase();
      const status: ImportUserRow['status'] = rawStatus === 'INACTIVE' ? 'Inactive' : 'Active';

      if (!validRoles.includes(role)) {
        throw new Error(`Invalid role found: ${role || 'blank'}.`);
      }

      return {
        name: row[nameIndex]?.trim() ?? '',
        email: row[emailIndex]?.trim() ?? '',
        password: row[passwordIndex]?.trim() ?? '',
        role,
        status,
      };
    }).filter(row => row.name && row.email && row.password.length >= 8);
  }

  private parseCsvRows(csv: string): string[][] {
    const rows: string[][] = [];
    let row: string[] = [];
    let value = '';
    let quoted = false;

    for (let index = 0; index < csv.length; index++) {
      const char = csv[index];
      const next = csv[index + 1];

      if (char === '"' && quoted && next === '"') {
        value += '"';
        index++;
      } else if (char === '"') {
        quoted = !quoted;
      } else if (char === ',' && !quoted) {
        row.push(value);
        value = '';
      } else if ((char === '\n' || char === '\r') && !quoted) {
        if (char === '\r' && next === '\n') {
          index++;
        }
        row.push(value);
        rows.push(row);
        row = [];
        value = '';
      } else {
        value += char;
      }
    }

    row.push(value);
    rows.push(row);
    return rows;
  }

  private showMessage(message: string): void {
    this.snackBar.open(message, '×', {
      duration: 3500,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: 'app-snackbar-panel',
    });
  }
}
