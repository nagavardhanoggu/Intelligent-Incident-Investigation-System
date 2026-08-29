import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { IncidentService } from '../../../services/incident.service';
import { SeverityChipComponent } from '../../../shared/components/severity-chip/severity-chip.component';
import { AuthService } from '../../../core/services/auth.service';
import { Incident, IncidentStatus, Priority } from '../../../models/incident.model';
import { IncidentCreateDialogComponent } from '../create-incident/incident-create-dialog.component';

interface IncidentFilters {
  query: string;
  priority: Priority | 'ALL';
  status: IncidentStatus | 'ALL';
  assignee: string;
}

@Component({
  selector: 'app-incident-list',
  imports: [
    RouterLink,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
    MatSnackBarModule,
    MatTableModule,
    MatTooltipModule,
    SeverityChipComponent,
  ],
  templateUrl: './incident-list.component.html',
  styleUrl: './incident-list.component.scss',
})
export class IncidentListComponent {
  private readonly incidentService = inject(IncidentService);
  private readonly auth = inject(AuthService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);
  private readonly incidents = toSignal(this.incidentService.listIncidents(), { initialValue: [] });
  readonly priorityOptions: Priority[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  readonly statusOptions: IncidentStatus[] = ['OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED'];
  readonly filters = signal<IncidentFilters>({
    query: '',
    priority: 'ALL',
    status: 'ALL',
    assignee: 'ALL',
  });
  readonly assigneeOptions = computed(() =>
    Array.from(new Set(this.incidents().map(incident => incident.assignedUser))).sort(),
  );
  readonly filteredIncidents = computed(() => {
    const filters = this.filters();
    const query = filters.query.trim().toLowerCase();

    return this.incidents().filter(incident => {
      const matchesQuery =
        !query ||
        `${incident.incidentKey} ${incident.title} ${incident.description} ${incident.assignedUser}`
          .toLowerCase()
          .includes(query);
      const matchesPriority = filters.priority === 'ALL' || incident.priority === filters.priority;
      const matchesStatus = filters.status === 'ALL' || incident.status === filters.status;
      const matchesAssignee = filters.assignee === 'ALL' || incident.assignedUser === filters.assignee;

      return matchesQuery && matchesPriority && matchesStatus && matchesAssignee;
    });
  });
  readonly columns = ['incidentKey', 'title', 'priority', 'status', 'assignedUser', 'createdAt', 'actions'];

  canCreateIncident(): boolean {
    return this.auth.hasAnyPermission(['incidents:create']);
  }

  canEditIncident(): boolean {
    return this.auth.hasAnyPermission(['incidents:update_any', 'incidents:update_assigned']);
  }

  canDeleteIncident(): boolean {
    return this.auth.hasAnyPermission(['incidents:delete']);
  }

  editIncident(incident: Incident): void {
    if (!this.canEditIncident()) {
      return;
    }

    const dialogRef = this.dialog.open(IncidentCreateDialogComponent, {
      width: '720px',
      maxWidth: 'calc(100vw - 32px)',
      panelClass: 'incident-create-dialog-panel',
      backdropClass: 'app-dialog-backdrop',
      autoFocus: false,
      restoreFocus: false,
      data: {
        mode: 'edit',
        incident,
      },
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result?.mode === 'edit' && result.incidentId) {
        this.incidentService.updateIncident(result.incidentId, result.value);
      }
    });
  }

  deleteIncident(incident: Incident): void {
    if (!this.canDeleteIncident()) {
      return;
    }

    this.incidentService.deleteIncident(incident.id);
    this.snackBar.open(`${incident.incidentKey} deleted`, '×', {
      duration: 3000,
      horizontalPosition: 'right',
      verticalPosition: 'top',
      panelClass: 'app-snackbar-panel',
    });
  }

  updateQuery(event: Event): void {
    this.filters.update(filters => ({
      ...filters,
      query: (event.target as HTMLInputElement).value,
    }));
  }

  updatePriority(priority: Priority | 'ALL'): void {
    this.filters.update(filters => ({ ...filters, priority }));
  }

  updateStatus(status: IncidentStatus | 'ALL'): void {
    this.filters.update(filters => ({ ...filters, status }));
  }

  updateAssignee(assignee: string): void {
    this.filters.update(filters => ({ ...filters, assignee }));
  }

  clearFilters(): void {
    this.filters.set({
      query: '',
      priority: 'ALL',
      status: 'ALL',
      assignee: 'ALL',
    });
  }
}
