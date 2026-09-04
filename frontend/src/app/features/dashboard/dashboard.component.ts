import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Chart } from 'chart.js/auto';
import type { ChartOptions } from 'chart.js';

import { AuthService } from '../../core/services/auth.service';
import { SeverityChipComponent } from '../../shared/components/severity-chip/severity-chip.component';

interface DashboardData {
  sectionHeadings?: {
    kpis?: DashboardSectionHeading;
    serviceHealth?: DashboardSectionHeading;
    incidentTrends?: DashboardSectionHeading;
    rootCauseDistribution?: DashboardSectionHeading;
    priorityBreakdown?: DashboardSectionHeading;
    assignmentGroups?: DashboardSectionHeading;
    recentCauses?: DashboardSectionHeading;
    activeQueue?: DashboardSectionHeading;
    anomalySignals?: DashboardSectionHeading;
    controlActions?: DashboardSectionHeading;
    recommendedActions?: DashboardSectionHeading;
  };
  totalIncidents: number;
  openIncidents: number;
  closedIncidents: number;
  criticalIncidents: number;
  kpiCards?: DashboardSummaryCard[];
  serviceHealth: DashboardSummaryCard[];
  priorityBreakdown: { label: string; value: number }[];
  assignmentGroups: { name: string; incidents: number }[];
  recentCauses: { cause: string; count: number; confidence: string }[];
  activeQueue: { key: string; service: string; priority: string; status: string; owner: string; mttr: string }[];
  anomalySignals: { metric: string; value: string; source: string; severity: string }[];
  actionItems: string[];
  trend: { label: string; incidents: number }[];
  rootCauseDistribution: { cause: string; count: number }[];
}

interface DashboardSectionHeading {
  title: string;
  subtitle: string;
  icon: string;
}

interface DashboardSummaryCard {
  label: string;
  value: string;
  helper?: string;
  trend?: string;
  icon?: string;
}

@Component({
  selector: 'app-dashboard',
  imports: [MatCardModule, MatIconModule, SeverityChipComponent],
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
  private readonly rerenderChartsForTheme = () => {
    if (this.viewReady && this.data) {
      this.renderCharts();
    }
  };

  kpiCards: DashboardSummaryCard[] = [];
  serviceHealth: DashboardData['serviceHealth'] = [];
  priorityBreakdown: DashboardData['priorityBreakdown'] = [];
  assignmentGroups: DashboardData['assignmentGroups'] = [];
  recentCauses: DashboardData['recentCauses'] = [];
  activeQueue: DashboardData['activeQueue'] = [];
  anomalySignals: DashboardData['anomalySignals'] = [];
  actionItems: string[] = [];
  sectionHeadings: Required<NonNullable<DashboardData['sectionHeadings']>> = {
    kpis: {
      title: 'Incident Overview',
      subtitle: 'Current incident records from the database.',
      icon: 'dashboard',
    },
    serviceHealth: {
      title: 'Service Health Signals',
      subtitle: 'Operational telemetry summarized from stored metrics.',
      icon: 'monitoring',
    },
    incidentTrends: {
      title: 'Incident Trends',
      subtitle: 'Incident volume grouped by created month from the incident database.',
      icon: 'show_chart',
    },
    rootCauseDistribution: {
      title: 'Root Cause Distribution',
      subtitle: 'Confirmed root-cause categories from resolved incident records.',
      icon: 'donut_large',
    },
    priorityBreakdown: {
      title: 'Open Incidents by Priority',
      subtitle: 'Active incidents grouped by priority.',
      icon: 'priority_high',
    },
    assignmentGroups: {
      title: 'Top Assignment Groups',
      subtitle: 'Incident ownership by assigned users and queues.',
      icon: 'groups',
    },
    recentCauses: {
      title: 'Recent ML Root Causes',
      subtitle: 'Predicted causes compared with confirmed records.',
      icon: 'psychology',
    },
    activeQueue: {
      title: 'Active Investigation Queue',
      subtitle: 'Open incidents currently assigned for investigation.',
      icon: 'manage_search',
    },
    anomalySignals: {
      title: 'Anomaly Signals',
      subtitle: 'Peak metric values detected from stored telemetry.',
      icon: 'sensors',
    },
    controlActions: {
      title: 'Operational Control Actions',
      subtitle: 'Prevention actions from resolution records.',
      icon: 'tune',
    },
    recommendedActions: {
      title: 'Recommended Actions',
      subtitle: 'Prevention actions from resolution records.',
      icon: 'task_alt',
    },
  };

  canViewInvestigationWidgets(): boolean {
    return this.auth.hasAnyPermission(['dashboard:admin', 'dashboard:investigator']);
  }

  canViewAdminWidgets(): boolean {
    return this.auth.hasAnyPermission(['dashboard:admin']);
  }

  actionHeading(): DashboardSectionHeading {
    return this.canViewAdminWidgets() ? this.sectionHeadings.controlActions : this.sectionHeadings.recommendedActions;
  }

  ngOnInit(): void {
    this.http.get<DashboardData>(`${this.apiUrl}/dashboard/summary`).subscribe(data => {
      this.data = data;
      this.kpiCards = data.kpiCards ?? [
        { label: 'Total Incidents', value: String(data.totalIncidents), helper: 'All incident records', icon: 'receipt_long' },
        { label: 'Open Incidents', value: String(data.openIncidents), helper: 'Open and investigating', icon: 'pending_actions' },
        { label: 'Closed Incidents', value: String(data.closedIncidents), helper: 'Resolved and closed', icon: 'verified' },
        { label: 'Critical Incidents', value: String(data.criticalIncidents), helper: 'Priority marked critical', icon: 'warning' },
      ];
      this.serviceHealth = data.serviceHealth;
      this.priorityBreakdown = data.priorityBreakdown;
      this.assignmentGroups = data.assignmentGroups;
      this.recentCauses = data.recentCauses;
      this.activeQueue = data.activeQueue;
      this.anomalySignals = data.anomalySignals;
      this.actionItems = data.actionItems;
      this.sectionHeadings = {
        kpis: data.sectionHeadings?.kpis ?? this.sectionHeadings.kpis,
        serviceHealth: data.sectionHeadings?.serviceHealth ?? this.sectionHeadings.serviceHealth,
        incidentTrends: data.sectionHeadings?.incidentTrends ?? this.sectionHeadings.incidentTrends,
        rootCauseDistribution: data.sectionHeadings?.rootCauseDistribution ?? this.sectionHeadings.rootCauseDistribution,
        priorityBreakdown: data.sectionHeadings?.priorityBreakdown ?? this.sectionHeadings.priorityBreakdown,
        assignmentGroups: data.sectionHeadings?.assignmentGroups ?? this.sectionHeadings.assignmentGroups,
        recentCauses: data.sectionHeadings?.recentCauses ?? this.sectionHeadings.recentCauses,
        activeQueue: data.sectionHeadings?.activeQueue ?? this.sectionHeadings.activeQueue,
        anomalySignals: data.sectionHeadings?.anomalySignals ?? this.sectionHeadings.anomalySignals,
        controlActions: data.sectionHeadings?.controlActions ?? this.sectionHeadings.controlActions,
        recommendedActions: data.sectionHeadings?.recommendedActions ?? this.sectionHeadings.recommendedActions,
      };
      if (this.viewReady) {
        queueMicrotask(() => this.renderCharts());
      }
    });
  }

  ngAfterViewInit(): void {
    this.viewReady = true;
    window.addEventListener('iiis-theme-change', this.rerenderChartsForTheme);
    if (this.data) {
      this.renderCharts();
    }
  }

  ngOnDestroy(): void {
    window.removeEventListener('iiis-theme-change', this.rerenderChartsForTheme);
    this.charts.forEach(chart => chart.destroy());
  }

  private renderCharts(): void {
    if (!this.data) {
      return;
    }
    this.charts.forEach(chart => chart.destroy());
    const colors = this.chartColors();
    this.charts = [
      new Chart(this.trend.nativeElement, {
        type: 'line',
        data: {
          labels: this.data.trend.map(item => item.label),
          datasets: [
            {
              label: 'Incidents',
              data: this.data.trend.map(item => item.incidents),
              borderColor: colors.accent,
              backgroundColor: colors.accentFill,
              pointBackgroundColor: colors.accent,
              pointBorderColor: colors.surface,
              tension: 0.35,
            },
          ],
        },
        options: this.chartOptions(),
      }),
      new Chart(this.causes.nativeElement, {
        type: 'bar',
        data: {
          labels: this.data.rootCauseDistribution.map(item => item.cause),
          datasets: [{ label: 'Root Causes', data: this.data.rootCauseDistribution.map(item => item.count), backgroundColor: colors.accent }],
        },
        options: this.chartOptions(),
      }),
    ];
  }

  private chartOptions(): ChartOptions {
    const colors = this.chartColors();

    return {
      plugins: {
        legend: {
          labels: {
            color: colors.text,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: colors.muted,
          },
          grid: {
            color: colors.grid,
          },
          border: {
            color: colors.border,
          },
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: colors.muted,
          },
          grid: {
            color: colors.grid,
          },
          border: {
            color: colors.border,
          },
        },
      },
    };
  }

  private chartColors(): { text: string; muted: string; grid: string; border: string; accent: string; accentFill: string; surface: string } {
    const isDark = document.documentElement.dataset['theme'] === 'dark';

    return isDark
      ? {
          text: '#f8fafc',
          muted: '#b8c4d4',
          grid: 'rgba(184, 196, 212, 0.16)',
          border: '#333b48',
          accent: '#ff704a',
          accentFill: 'rgba(255, 112, 74, 0.18)',
          surface: '#181b21',
        }
      : {
          text: '#17202a',
          muted: '#667085',
          grid: 'rgba(102, 112, 133, 0.18)',
          border: '#e4e7ec',
          accent: '#f04b23',
          accentFill: 'rgba(240, 75, 35, 0.14)',
          surface: '#ffffff',
        };
  }
}
