import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { Chart } from 'chart.js/auto';

import { AuthService } from '../../core/services/auth.service';

interface DashboardData {
  totalIncidents: number;
  openIncidents: number;
  closedIncidents: number;
  criticalIncidents: number;
  serviceHealth: { label: string; value: string; trend: string }[];
  priorityBreakdown: { label: string; value: number }[];
  assignmentGroups: { name: string; incidents: number }[];
  recentCauses: { cause: string; count: number; confidence: string }[];
  activeQueue: { key: string; service: string; priority: string; status: string; owner: string; mttr: string }[];
  anomalySignals: { metric: string; value: string; source: string; severity: string }[];
  actionItems: string[];
  trend: { label: string; incidents: number }[];
  rootCauseDistribution: { cause: string; count: number }[];
}

@Component({
  selector: 'app-dashboard',
  imports: [MatCardModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements AfterViewInit, OnDestroy, OnInit {
  @ViewChild('trend') trend!: ElementRef<HTMLCanvasElement>;
  @ViewChild('causes') causes!: ElementRef<HTMLCanvasElement>;
  private readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private charts: Chart[] = [];
  private viewReady = false;
  private data: DashboardData | null = null;

  kpis = { total: 0, open: 0, closed: 0, critical: 0 };
  serviceHealth: DashboardData['serviceHealth'] = [];
  priorityBreakdown: DashboardData['priorityBreakdown'] = [];
  assignmentGroups: DashboardData['assignmentGroups'] = [];
  recentCauses: DashboardData['recentCauses'] = [];
  activeQueue: DashboardData['activeQueue'] = [];
  anomalySignals: DashboardData['anomalySignals'] = [];
  actionItems: string[] = [];

  canViewInvestigationWidgets(): boolean {
    return this.auth.hasAnyPermission(['dashboard:admin', 'dashboard:investigator']);
  }

  canViewAdminWidgets(): boolean {
    return this.auth.hasAnyPermission(['dashboard:admin']);
  }

  ngOnInit(): void {
    this.http.get<DashboardData>(`${this.apiUrl}/dashboard/summary`).subscribe(data => {
      this.data = data;
      this.kpis = {
        total: data.totalIncidents,
        open: data.openIncidents,
        closed: data.closedIncidents,
        critical: data.criticalIncidents,
      };
      this.serviceHealth = data.serviceHealth;
      this.priorityBreakdown = data.priorityBreakdown;
      this.assignmentGroups = data.assignmentGroups;
      this.recentCauses = data.recentCauses;
      this.activeQueue = data.activeQueue;
      this.anomalySignals = data.anomalySignals;
      this.actionItems = data.actionItems;
      if (this.viewReady) {
        queueMicrotask(() => this.renderCharts());
      }
    });
  }

  ngAfterViewInit(): void {
    this.viewReady = true;
    if (this.data) {
      this.renderCharts();
    }
  }

  ngOnDestroy(): void {
    this.charts.forEach(chart => chart.destroy());
  }

  private renderCharts(): void {
    if (!this.data) {
      return;
    }
    this.charts.forEach(chart => chart.destroy());
    this.charts = [
      new Chart(this.trend.nativeElement, {
        type: 'line',
        data: {
          labels: this.data.trend.map(item => item.label),
          datasets: [{ label: 'Incidents', data: this.data.trend.map(item => item.incidents), borderColor: '#f04b23', tension: 0.35 }],
        },
      }),
      new Chart(this.causes.nativeElement, {
        type: 'bar',
        data: {
          labels: this.data.rootCauseDistribution.map(item => item.cause),
          datasets: [{ label: 'Root Causes', data: this.data.rootCauseDistribution.map(item => item.count), backgroundColor: '#f04b23' }],
        },
      }),
    ];
  }
}
