export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type IncidentStatus = 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'CLOSED';
export type Cause =
  | 'Deployment Failure'
  | 'Database Issue'
  | 'Network Issue'
  | 'Memory Leak'
  | 'Application Failure';

export interface Incident {
  id: number;
  incidentKey: string;
  title: string;
  description: string;
  priority: Priority;
  impact: 'LOW' | 'MEDIUM' | 'HIGH';
  urgency: 'LOW' | 'MEDIUM' | 'HIGH';
  status: IncidentStatus;
  assignedUser: string;
  createdAt: string;
  updatedAt: string;
}

export interface MetricPoint {
  capturedAt: string;
  cpuUsage: number;
  memoryUsage: number;
  responseTimeMs: number;
  errorRate: number;
}

export interface TimelineEvent {
  eventTime: string;
  eventType: string;
  description: string;
  source: string;
}

export interface Prediction {
  predictedCause: Cause;
  confidenceScore: number;
  modelVersion: string;
  recommendedActions: string[];
}

export interface Resolution {
  id: number;
  incidentTitle: string;
  rootCause: Cause;
  resolution: string;
  preventionSteps: string;
  updatedAt: string;
}
