import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface FeaturePageKpi {
  label: string;
  value: string;
  helper: string;
  icon: string;
  state?: string;
}

export interface FeaturePagePill {
  icon: string;
  label: string;
}

export interface FeaturePageItem {
  title: string;
  subtitle?: string;
  detail: string;
  meta?: string;
  status?: string;
  icon?: string;
  progress?: number;
  tags?: string[];
  route?: string;
}

export interface FeaturePageSection {
  title: string;
  caption?: string;
  items: FeaturePageItem[];
}

export interface FeaturePageData {
  title: string;
  subtitle: string;
  pill?: FeaturePagePill;
  kpis: FeaturePageKpi[];
  sections: FeaturePageSection[];
}

@Injectable({ providedIn: 'root' })
export class FeaturePageService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';

  getPage(pageKey: string): Observable<FeaturePageData> {
    return this.http.get<FeaturePageData>(`${this.apiUrl}/feature-pages/${pageKey}`);
  }
}
