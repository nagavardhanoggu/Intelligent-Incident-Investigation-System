import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
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

type PredictionOptionKey =
  | 'priority'
  | 'impact'
  | 'urgency'
  | 'sla_status'
  | 'category'
  | 'subcategory'
  | 'u_symptom'
  | 'assignment_group'
  | 'contact_type'
  | 'knowledge';

type PredictionOptions = Record<PredictionOptionKey, string[]>;

interface PredictionOptionsResponse {
  defaults?: Record<string, string | number>;
  options?: Partial<PredictionOptions>;
}

const emptyPredictionOptions = (): PredictionOptions => ({
  priority: [],
  impact: [],
  urgency: [],
  sla_status: [],
  category: [],
  subcategory: [],
  u_symptom: [],
  assignment_group: [],
  contact_type: [],
  knowledge: [],
});

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
export class MlTrainingComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly minimumLoadingMs = 5000;

  readonly prediction = signal<PredictionResult | null>(null);
  readonly predictionError = signal('');
  readonly loading = signal(false);
  readonly optionsLoading = signal(false);
  readonly optionsError = signal('');
  readonly predictionOptions = signal<PredictionOptions>(emptyPredictionOptions());

  readonly predictionForm = this.fb.nonNullable.group({
    priority: ['', Validators.required],
    impact: ['', Validators.required],
    urgency: ['', Validators.required],
    reassignment_count: [5, [Validators.required, Validators.min(0)]],
    reopen_count: [3, [Validators.required, Validators.min(0)]],
    sla_status: ['', Validators.required],
    category: ['', Validators.required],
    subcategory: ['', Validators.required],
    u_symptom: ['', Validators.required],
    assignment_group: ['', Validators.required],
    contact_type: ['', Validators.required],
    knowledge: ['', Validators.required],
    sys_mod_count: [4, [Validators.required, Validators.min(0)]],
  });

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

  ngOnInit(): void {
    this.loadPredictionOptions();
  }

  analyzeIncident(): void {
    if (this.predictionForm.invalid || this.optionsLoading()) {
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

  formatOption(option: string): string {
    return option
      .replace(/_/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, character => character.toUpperCase());
  }

  private loadPredictionOptions(): void {
    this.optionsLoading.set(true);
    this.optionsError.set('');
    this.http.get<PredictionOptionsResponse>(`${this.apiUrl}/predict/options`).subscribe({
      next: (data) => {
        const options = data.options ?? {};
        this.predictionOptions.set({
          priority: options.priority ?? [],
          impact: options.impact ?? [],
          urgency: options.urgency ?? [],
          sla_status: options.sla_status ?? [],
          category: options.category ?? [],
          subcategory: options.subcategory ?? [],
          u_symptom: options.u_symptom ?? [],
          assignment_group: options.assignment_group ?? [],
          contact_type: options.contact_type ?? [],
          knowledge: options.knowledge ?? [],
        });
        this.applyDefaults(data.defaults ?? {});
        this.optionsLoading.set(false);
      },
      error: (error: HttpErrorResponse) => {
        if (error.status === 401) {
          this.optionsError.set('Your session has expired. Please sign in again.');
        } else if (error.status === 403) {
          this.optionsError.set('Your role does not have permission to load ML prediction fields.');
        } else {
          this.optionsError.set('Prediction fields could not be loaded from the backend.');
        }
        this.optionsLoading.set(false);
      },
    });
  }

  private applyDefaults(defaults: Record<string, string | number>): void {
    this.predictionForm.patchValue({
      priority: this.asString(defaults['priority']),
      impact: this.asString(defaults['impact']),
      urgency: this.asString(defaults['urgency']),
      reassignment_count: this.asNumber(defaults['reassignment_count']),
      reopen_count: this.asNumber(defaults['reopen_count']),
      sla_status: this.asString(defaults['sla_status']),
      category: this.asString(defaults['category']),
      subcategory: this.asString(defaults['subcategory']),
      u_symptom: this.asString(defaults['u_symptom']),
      assignment_group: this.asString(defaults['assignment_group']),
      contact_type: this.asString(defaults['contact_type']),
      knowledge: this.asString(defaults['knowledge']),
      sys_mod_count: this.asNumber(defaults['sys_mod_count']),
    });
  }

  private asString(value: string | number | undefined): string {
    return typeof value === 'string' ? value : '';
  }

  private asNumber(value: string | number | undefined): number {
    const parsed = Number(value ?? 0);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  private finishLoading(startedAt: number, callback: () => void): void {
    const remainingMs = Math.max(this.minimumLoadingMs - (Date.now() - startedAt), 0);
    window.setTimeout(() => {
      callback();
      this.loading.set(false);
    }, remainingMs);
  }
}
