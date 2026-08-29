import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Incident } from '../models/incident.model';

export interface InvestigationTimelineItem {
  id: number;
  eventTime: string;
  eventType: string;
  description: string;
  source: string;
}

export interface InvestigationMetricItem {
  id: number;
  capturedAt: string;
  cpuUsage: number | null;
  memoryUsage: number | null;
  diskUsage: number | null;
  responseTimeMs: number | null;
  errorRate: number | null;
  databaseConnections: number | null;
}

export interface InvestigationLogItem {
  id: number;
  incidentId: number;
  fileName: string;
  fileType: string;
  storagePath: string;
  uploadedAt: string;
  parsedContent: string | null;
}

export interface InvestigationPredictionItem {
  id: number;
  predictedCause: string;
  confidenceScore: number;
  modelVersion: string;
  predictedAt: string;
  modelFeatures: Record<string, string | number | boolean | null>;
}

export interface InvestigationWorkspace {
  incident: Incident;
  summary: {
    signalCount: number;
    logCount: number;
    metricCount: number;
    timelineCount: number;
    riskLevel: string;
  };
  timeline: InvestigationTimelineItem[];
  metrics: InvestigationMetricItem[];
  logs: InvestigationLogItem[];
  prediction: InvestigationPredictionItem | null;
  recommendedActions: string[];
  similarIncidentKeys: string[];
}

@Injectable({ providedIn: 'root' })
export class InvestigationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';

  getWorkspace(incidentId: number): Observable<InvestigationWorkspace> {
    return this.http.get<InvestigationWorkspace>(`${this.apiUrl}/investigations/${incidentId}`);
  }
}
