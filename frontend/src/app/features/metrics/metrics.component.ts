import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { Chart } from 'chart.js/auto';

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
    const labels = this.data.chart.labels.map(value => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    this.charts = [
      new Chart(this.resourceChart.nativeElement, {
        type: 'line',
        data: {
          labels,
          datasets: [
            { label: 'CPU %', data: this.data.chart.cpu, borderColor: '#f04b23', tension: 0.35 },
            { label: 'Memory %', data: this.data.chart.memory, borderColor: '#16a34a', tension: 0.35 },
          ],
        },
      }),
      new Chart(this.latencyChart.nativeElement, {
        type: 'bar',
        data: {
          labels,
          datasets: [{ label: 'Response Time ms', data: this.data.chart.responseTime, backgroundColor: '#f04b23' }],
        },
      }),
    ];
  }
}
