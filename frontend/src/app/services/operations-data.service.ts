import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface OperationKpi {
  label: string;
  value: string;
  helper: string;
  icon: string;
}

export interface OperationListItem {
  name: string;
  detail: string;
  owner: string;
  status: string;
  icon: string;
}

export interface OperationSideItem {
  title: string;
  detail: string;
}

@Injectable({ providedIn: 'root' })
export class OperationsDataService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';

  getPage<T>(pageKey: string): Observable<T> {
    return this.http.get<T>(`${this.apiUrl}/operations/${pageKey}`);
  }
}
