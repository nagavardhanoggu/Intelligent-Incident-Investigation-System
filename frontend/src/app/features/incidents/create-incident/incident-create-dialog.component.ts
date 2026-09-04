import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { Incident } from '../../../models/incident.model';
import { IncidentAssignee, IncidentFieldOptions, IncidentService } from '../../../services/incident.service';

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

const emptyIncidentFieldOptions = (): IncidentFieldOptions['options'] => ({
  priority: [],
  impact: [],
  urgency: [],
  status: [],
});

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
  readonly fieldOptions = signal<IncidentFieldOptions['options']>(emptyIncidentFieldOptions());
  readonly optionsLoading = signal(false);
  readonly optionsError = signal('');

  readonly form = this.fb.nonNullable.group({
    title: [this.data?.incident?.title ?? '', Validators.required],
    description: [this.data?.incident?.description ?? '', Validators.required],
    priority: [this.data?.incident?.priority ?? '', Validators.required],
    impact: [this.data?.incident?.impact ?? '', Validators.required],
    urgency: [this.data?.incident?.urgency ?? '', Validators.required],
    assignedUserId: this.fb.control<number | null>(null),
  });

  ngOnInit(): void {
    this.optionsLoading.set(true);
    this.incidentService.getIncidentOptions().subscribe({
      next: data => {
        this.fieldOptions.set({
          priority: data.options.priority ?? [],
          impact: data.options.impact ?? [],
          urgency: data.options.urgency ?? [],
          status: data.options.status ?? [],
        });
        this.applyDefaults(data.defaults);
        this.optionsLoading.set(false);
      },
      error: () => {
        this.optionsError.set('Incident field options could not be loaded.');
        this.optionsLoading.set(false);
      },
    });

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
    if (this.form.invalid || this.optionsLoading()) {
      this.form.markAllAsTouched();
      return;
    }

    this.dialogRef.close({
      mode: this.isEdit ? 'edit' : 'create',
      incidentId: this.data?.incident?.id,
      value: this.form.getRawValue() as IncidentCreateValue,
    });
  }

  private applyDefaults(defaults: IncidentFieldOptions['defaults']): void {
    if (this.isEdit) {
      return;
    }

    this.form.patchValue({
      priority: this.optionDefault(defaults.priority, this.fieldOptions().priority),
      impact: this.optionDefault(defaults.impact, this.fieldOptions().impact),
      urgency: this.optionDefault(defaults.urgency, this.fieldOptions().urgency),
    });
  }

  private optionDefault<T extends string>(value: string | undefined, options: T[]): T | '' {
    if (value && options.includes(value as T)) {
      return value as T;
    }
    return options[0] ?? '';
  }
}
