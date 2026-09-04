import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, catchError, of } from 'rxjs';

import { Incident } from '../models/incident.model';

export interface IncidentAssignee {
  id: number;
  fullName: string;
  role: string;
}

export interface IncidentPayload {
  title: string;
  description: string;
  priority: Incident['priority'];
  impact: Incident['impact'];
  urgency: Incident['urgency'];
  assignedUserId: number | null;
}

export interface IncidentFieldOptions {
  defaults: Partial<Record<'priority' | 'impact' | 'urgency' | 'status', string>>;
  options: {
    priority: Incident['priority'][];
    impact: Incident['impact'][];
    urgency: Incident['urgency'][];
    status: Incident['status'][];
  };
}

@Injectable({ providedIn: 'root' })
export class IncidentService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private readonly incidentsSubject = new BehaviorSubject<Incident[]>([]);
  private loaded = false;

  listIncidents(): Observable<Incident[]> {
    if (!this.loaded) {
      this.reload();
    }
    return this.incidentsSubject.asObservable();
  }

  reload(): void {
    this.http.get<Incident[]>(`${this.apiUrl}/incidents`).subscribe({
      next: incidents => {
        this.loaded = true;
        this.incidentsSubject.next(incidents);
      },
      error: () => this.incidentsSubject.next([]),
    });
  }

  getIncident(id: number): Observable<Incident | undefined> {
    return this.http
      .get<Incident>(`${this.apiUrl}/incidents/${id}`)
      .pipe(catchError(() => of(undefined)));
  }

  createIncident(payload: IncidentPayload): void {
    this.http.post<Incident>(`${this.apiUrl}/incidents`, payload).subscribe(incident => {
      this.incidentsSubject.next([incident, ...this.incidentsSubject.value]);
    });
  }

  updateIncident(id: number, payload: IncidentPayload): void {
    this.http.put<Incident>(`${this.apiUrl}/incidents/${id}`, payload).subscribe(updated => {
      this.incidentsSubject.next(
        this.incidentsSubject.value.map(incident => incident.id === id ? updated : incident),
      );
    });
  }

  deleteIncident(id: number): void {
    this.http.delete(`${this.apiUrl}/incidents/${id}`).subscribe(() => {
      this.incidentsSubject.next(this.incidentsSubject.value.filter(incident => incident.id !== id));
    });
  }

  listAssignees(): Observable<IncidentAssignee[]> {
    return this.http.get<IncidentAssignee[]>(`${this.apiUrl}/users/assignees`);
  }

  getIncidentOptions(): Observable<IncidentFieldOptions> {
    return this.http.get<IncidentFieldOptions>(`${this.apiUrl}/incidents/options`);
  }
}
