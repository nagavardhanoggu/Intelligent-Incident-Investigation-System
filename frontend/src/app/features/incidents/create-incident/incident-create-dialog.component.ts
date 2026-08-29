import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { Incident } from '../../../models/incident.model';
import { IncidentAssignee, IncidentService } from '../../../services/incident.service';

export interface IncidentCreateValue {
  title: string;
  description: string;
  priority: Incident['priority'];
  impact: Incident['impact'];
  urgency: Incident['urgency'];
  assignedUserId: number | null;
}

export interface IncidentDialogData {
  mode: 'create' | 'edit';
  incident?: Incident;
}

export interface IncidentDialogResult {
  mode: 'create' | 'edit';
  incidentId?: number;
  value: IncidentCreateValue;
}

@Component({
  selector: 'app-incident-create-dialog',
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
  ],
  templateUrl: './incident-create-dialog.component.html',
  styleUrl: './incident-create-dialog.component.scss',
})
export class IncidentCreateDialogComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly incidentService = inject(IncidentService);
  private readonly dialogRef = inject(MatDialogRef<IncidentCreateDialogComponent, IncidentDialogResult>);
  readonly data = inject<IncidentDialogData | null>(MAT_DIALOG_DATA, { optional: true });
  readonly isEdit = this.data?.mode === 'edit';
  readonly assignees = signal<IncidentAssignee[]>([]);

  readonly form = this.fb.nonNullable.group({
    title: [this.data?.incident?.title ?? '', Validators.required],
    description: [this.data?.incident?.description ?? '', Validators.required],
    priority: [this.data?.incident?.priority ?? 'HIGH', Validators.required],
    impact: [this.data?.incident?.impact ?? 'HIGH', Validators.required],
    urgency: [this.data?.incident?.urgency ?? 'HIGH', Validators.required],
    assignedUserId: this.fb.control<number | null>(null),
  });

  ngOnInit(): void {
    this.incidentService.listAssignees().subscribe(assignees => {
      this.assignees.set(assignees);
      const assignedUser = this.data?.incident?.assignedUser;
      const selected = assignees.find(assignee => assignee.fullName === assignedUser) ?? assignees[0];
      this.form.controls.assignedUserId.setValue(selected?.id ?? null);
    });
  }

  close(): void {
    this.dialogRef.close();
  }

  createIncident(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.dialogRef.close({
      mode: this.isEdit ? 'edit' : 'create',
      incidentId: this.data?.incident?.id,
      value: this.form.getRawValue(),
    });
  }

}
