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
  detailKey?: string;
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
  parentTitle?: string;
}

export type FeaturePageSource = 'feature-pages' | 'operations';

@Injectable({ providedIn: 'root' })
export class FeaturePageService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';

  getPage(pageKey: string, source: FeaturePageSource = 'feature-pages'): Observable<FeaturePageData> {
    return this.http.get<FeaturePageData>(`${this.apiUrl}/${source}/${pageKey}`);
  }

  getSubpage(pageKey: string, subpageKey: string, source: FeaturePageSource = 'feature-pages'): Observable<FeaturePageData> {
    return this.http.get<FeaturePageData>(`${this.apiUrl}/${source}/${pageKey}/subpages/${subpageKey}`);
  }
}
