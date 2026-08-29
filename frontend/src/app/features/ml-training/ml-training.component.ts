import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';

interface ProbableCause {
  cause: string;
  probability: number;
}

interface PredictionResult {
  incidentId?: number | null;
  predictedCause: string;
  confidenceScore: number;
  modelVersion: string;
  recommendedActions: string[];
  topProbableCauses: ProbableCause[];
  keyDecisionFactors: string[];
  predictionTime: string;
}

@Component({
  selector: 'app-ml-training',
  imports: [
    DatePipe,
    DecimalPipe,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './ml-training.component.html',
  styleUrl: './ml-training.component.scss',
})
export class MlTrainingComponent {
  private readonly fb = inject(FormBuilder);
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly minimumLoadingMs = 5000;

  readonly prediction = signal<PredictionResult | null>(null);
  readonly predictionError = signal('');
  readonly loading = signal(false);

  readonly predictionForm = this.fb.nonNullable.group({
    priority: ['Medium', Validators.required],
    impact: ['Medium', Validators.required],
    urgency: ['Medium', Validators.required],
    reassignment_count: [5, [Validators.required, Validators.min(0)]],
    reopen_count: [3, [Validators.required, Validators.min(0)]],
    sla_status: ['Met', Validators.required],
    category: ['Category 26', Validators.required],
    subcategory: ['Subcategory 174', Validators.required],
    u_symptom: ['Symptom 72', Validators.required],
    assignment_group: ['Group 56', Validators.required],
    contact_type: ['Phone', Validators.required],
    knowledge: ['True', Validators.required],
    sys_mod_count: [4, [Validators.required, Validators.min(0)]],
  });

  readonly priorityOptions = ['Low', 'Medium', 'High', 'Critical'];
  readonly impactOptions = ['Low', 'Medium', 'High', 'Critical'];
  readonly urgencyOptions = ['Low', 'Medium', 'High', 'Critical'];
  readonly slaOptions = ['Met', 'Breached', 'Pending'];
  readonly categoryOptions = ['Category 26', 'Category 42', 'Category 53', 'Category 46', 'Category 23'];
  readonly subcategoryOptions = ['Subcategory 174', 'Subcategory 223', 'Subcategory 175', 'Subcategory 164', 'Subcategory 9'];
  readonly symptomOptions = ['Symptom 72', 'Symptom 471', 'Symptom 87', 'Symptom 534', 'Symptom 4'];
  readonly assignmentGroupOptions = ['Group 56', 'Group 70', 'Group 24', 'Group 25', 'Group 39'];
  readonly contactTypeOptions = ['Phone', 'Self Service', 'Email', 'Direct Opening'];
  readonly knowledgeOptions = ['True', 'False'];

  readonly confidencePercent = computed(() => Math.round((this.prediction()?.confidenceScore ?? 0) * 100));
  readonly confidenceClass = computed(() => {
    const confidence = this.confidencePercent();
    if (confidence >= 75) {
      return 'high';
    }
    if (confidence >= 50) {
      return 'medium';
    }
    return 'low';
  });

  analyzeIncident(): void {
    if (this.predictionForm.invalid) {
      this.predictionForm.markAllAsTouched();
      return;
    }

    const startedAt = Date.now();
    this.loading.set(true);
    this.predictionError.set('');
    this.http.post<PredictionResult>(`${this.apiUrl}/predict`, this.predictionForm.getRawValue()).subscribe({
        next: (result) => {
          this.finishLoading(startedAt, () => this.prediction.set(result));
        },
        error: (error: HttpErrorResponse) => {
          this.finishLoading(startedAt, () => {
            this.prediction.set(null);
            if (error.status === 401) {
              this.predictionError.set('Your session has expired. Please sign in again.');
              return;
            }
            if (error.status === 403) {
              this.predictionError.set('Your role does not have permission to run ML predictions. Use Admin or Investigator access.');
              return;
            }
            if (error.status === 422) {
              this.predictionError.set('Please check the input values. All fields are required and counts must be zero or greater.');
              return;
            }
            this.predictionError.set('Prediction failed because the backend service is unavailable or returned an error.');
          });
        },
      });
  }

  private finishLoading(startedAt: number, callback: () => void): void {
    const remainingMs = Math.max(this.minimumLoadingMs - (Date.now() - startedAt), 0);
    window.setTimeout(() => {
      callback();
      this.loading.set(false);
    }, remainingMs);
  }
}
