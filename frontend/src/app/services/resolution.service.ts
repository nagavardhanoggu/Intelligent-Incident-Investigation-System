import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ResolutionArticle {
  id: number;
  incidentId: number;
  incidentTitle: string;
  rootCause: string;
  resolution: string;
  preventionSteps: string | null;
  updatedAt: string;
}

@Injectable({ providedIn: 'root' })
export class ResolutionService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';

  list(): Observable<ResolutionArticle[]> {
    return this.http.get<ResolutionArticle[]>(`${this.apiUrl}/resolutions`);
  }
}
