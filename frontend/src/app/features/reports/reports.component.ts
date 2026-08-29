import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { finalize } from 'rxjs';

import {
  MonthlyReportRow,
  ReportInsight,
  ReportKpis,
  ReportReviewItem,
  ReportsService,
} from '../../services/reports.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-reports',
  imports: [MatButtonModule, MatCardModule, MatIconModule, MatTableModule],
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss',
})
export class ReportsComponent implements OnInit {
  private readonly reportsService = inject(ReportsService);
  private readonly auth = inject(AuthService);

  readonly columns = ['month', 'incidents', 'critical', 'mttr', 'sla'];
  readonly kpis = signal<ReportKpis | null>(null);
  readonly rows = signal<MonthlyReportRow[]>([]);
  readonly insights = signal<ReportInsight[]>([]);
  readonly reviewItems = signal<ReportReviewItem[]>([]);
  readonly canExport = computed(() => this.auth.hasAnyPermission(['reports:export']));
  readonly loading = signal(true);
  readonly error = signal('');

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading.set(true);
    this.error.set('');

    this.reportsService
      .getSummary()
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: report => {
          this.kpis.set(report.kpis);
          this.rows.set(report.rows);
          this.insights.set(report.insights);
          this.reviewItems.set(report.reviewItems);
        },
        error: () => {
          this.kpis.set(null);
          this.rows.set([]);
          this.insights.set([]);
          this.reviewItems.set([]);
          this.error.set('Unable to load report data from the database.');
        },
      });
  }

  exportReport(): void {
    const reportKpis = this.kpis();
    const rows = this.rows();

    if (!reportKpis || !rows.length) {
      return;
    }

    const csvRows = [
      ['Metric', 'Value'],
      ['Average MTTR', reportKpis.averageMttr],
      ['SLA Compliance', reportKpis.slaCompliance],
      ['Repeat Incidents', String(reportKpis.repeatIncidents)],
      [],
      ['Month', 'Incidents', 'Critical', 'MTTR', 'SLA'],
      ...rows.map(row => [row.month, String(row.incidents), String(row.critical), row.mttr, row.sla]),
      [],
      ['Insight', 'Detail', 'Severity'],
      ...this.insights().map(item => [item.title, item.detail, item.severity]),
      [],
      ['Review Item', 'Detail'],
      ...this.reviewItems().map(item => [item.title, item.detail]),
    ];
    const csv = csvRows.map(row => row.map(value => this.escapeCsv(value)).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const link = document.createElement('a');

    link.href = url;
    link.download = 'incident-report-summary.csv';
    link.click();
    URL.revokeObjectURL(url);
  }

  private escapeCsv(value: string): string {
    return `"${value.replace(/"/g, '""')}"`;
  }
}
