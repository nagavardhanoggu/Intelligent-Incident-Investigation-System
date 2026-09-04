import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { Chart } from 'chart.js/auto';
import type { ChartOptions } from 'chart.js';

interface MetricsOverview {
  summary: { label: string; value: string; detail: string; icon: string; state: string }[];
  serviceHealth: { service: string; cpu: number; memory: number; latency: string; errors: string; status: string }[];
  thresholds: { metric: string; threshold: string; current: string; status: string }[];
  correlations: { time: string; signal: string; impact: string }[];
  chart: { labels: string[]; cpu: number[]; memory: number[]; responseTime: number[] };
}

@Component({
  selector: 'app-metrics',
  imports: [DatePipe, MatCardModule, MatChipsModule, MatIconModule, MatProgressBarModule],
  templateUrl: './metrics.component.html',
  styleUrl: './metrics.component.scss',
})
export class MetricsComponent implements AfterViewInit, OnDestroy, OnInit {
  @ViewChild('resourceChart') resourceChart!: ElementRef<HTMLCanvasElement>;
  @ViewChild('latencyChart') latencyChart!: ElementRef<HTMLCanvasElement>;
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private charts: Chart[] = [];
  private viewReady = false;
  private data: MetricsOverview | null = null;
  private readonly rerenderChartsForTheme = () => {
    if (this.viewReady && this.data) {
      this.renderCharts();
    }
  };

  summary: MetricsOverview['summary'] = [];
  serviceHealth: MetricsOverview['serviceHealth'] = [];
  thresholds: MetricsOverview['thresholds'] = [];
  correlations: MetricsOverview['correlations'] = [];

  ngOnInit(): void {
    this.http.get<MetricsOverview>(`${this.apiUrl}/metrics/overview`).subscribe(data => {
      this.data = data;
      this.summary = data.summary;
      this.serviceHealth = data.serviceHealth;
      this.thresholds = data.thresholds;
      this.correlations = data.correlations;
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
    const labels = this.data.chart.labels.map(value => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    const colors = this.chartColors();
    this.charts = [
      new Chart(this.resourceChart.nativeElement, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'CPU %',
              data: this.data.chart.cpu,
              borderColor: colors.accent,
              backgroundColor: colors.accentFill,
              pointBackgroundColor: colors.accent,
              pointBorderColor: colors.surface,
              tension: 0.35,
            },
            {
              label: 'Memory %',
              data: this.data.chart.memory,
              borderColor: colors.success,
              backgroundColor: colors.successFill,
              pointBackgroundColor: colors.success,
              pointBorderColor: colors.surface,
              tension: 0.35,
            },
          ],
        },
        options: this.chartOptions(),
      }),
      new Chart(this.latencyChart.nativeElement, {
        type: 'bar',
        data: {
          labels,
          datasets: [{ label: 'Response Time ms', data: this.data.chart.responseTime, backgroundColor: colors.accent }],
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

  private chartColors(): {
    text: string;
    muted: string;
    grid: string;
    border: string;
    accent: string;
    accentFill: string;
    success: string;
    successFill: string;
    surface: string;
  } {
    const isDark = document.documentElement.dataset['theme'] === 'dark';

    return isDark
      ? {
          text: '#f8fafc',
          muted: '#b8c4d4',
          grid: 'rgba(184, 196, 212, 0.16)',
          border: '#333b48',
          accent: '#ff704a',
          accentFill: 'rgba(255, 112, 74, 0.18)',
          success: '#34d399',
          successFill: 'rgba(52, 211, 153, 0.16)',
          surface: '#181b21',
        }
      : {
          text: '#17202a',
          muted: '#667085',
          grid: 'rgba(102, 112, 133, 0.18)',
          border: '#e4e7ec',
          accent: '#f04b23',
          accentFill: 'rgba(240, 75, 35, 0.14)',
          success: '#16a34a',
          successFill: 'rgba(22, 163, 74, 0.14)',
          surface: '#ffffff',
        };
  }
}
