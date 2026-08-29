import { Component, inject, signal } from '@angular/core';
import { AsyncPipe, DatePipe, DecimalPipe } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { catchError, map, of, switchMap, tap } from 'rxjs';
import { InvestigationMetricItem, InvestigationService } from '../../../services/investigation.service';

@Component({
  selector: 'app-investigation-workspace',
  imports: [AsyncPipe, DatePipe, DecimalPipe, MatCardModule, MatChipsModule, MatIconModule, MatListModule, MatProgressBarModule, MatTabsModule],
  templateUrl: './investigation-workspace.component.html',
  styleUrl: './investigation-workspace.component.scss',
})
export class InvestigationWorkspaceComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly investigationService = inject(InvestigationService);
  readonly loading = signal(true);
  readonly loadError = signal('');

  readonly workspace$ = this.route.paramMap.pipe(
    map(params => Number(params.get('id') ?? 0)),
    tap(() => {
      this.loading.set(true);
      this.loadError.set('');
    }),
    switchMap(id =>
      this.investigationService.getWorkspace(id).pipe(
        tap(() => this.loading.set(false)),
        catchError(() => {
          this.loading.set(false);
          this.loadError.set('Unable to load investigation workspace. Please sign in again or retry after the API is available.');
          return of(null);
        }),
      ),
    ),
  );

  metricValue(value: number | null, suffix = ''): string {
    return value === null || value === undefined ? 'N/A' : `${value}${suffix}`;
  }

  peakMetric(metrics: InvestigationMetricItem[], key: keyof InvestigationMetricItem): number {
    return Math.max(...metrics.map(metric => Number(metric[key] ?? 0)), 0);
  }

  confidencePercent(confidence: number): number {
    return Math.round(confidence * 100);
  }

  featureEntries(features: Record<string, string | number | boolean | null>): { key: string; value: string | number | boolean | null }[] {
    return Object.entries(features).map(([key, value]) => ({ key, value }));
  }
}
