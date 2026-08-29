import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ReportKpis {
  averageMttr: string;
  slaCompliance: string;
  repeatIncidents: number;
}

export interface MonthlyReportRow {
  month: string;
  incidents: number;
  critical: number;
  mttr: string;
  sla: string;
}

export interface ReportInsight {
  title: string;
  detail: string;
  severity: 'info' | 'warning' | 'critical';
  icon: string;
}

export interface ReportReviewItem {
  title: string;
  detail: string;
}

export interface ReportsResponse {
  kpis: ReportKpis;
  rows: MonthlyReportRow[];
  insights: ReportInsight[];
  reviewItems: ReportReviewItem[];
}

@Injectable({ providedIn: 'root' })
export class ReportsService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';

  getSummary(): Observable<ReportsResponse> {
    return this.http.get<ReportsResponse>(`${this.apiUrl}/reports/summary`);
  }
}
