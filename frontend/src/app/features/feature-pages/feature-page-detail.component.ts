import { NgClass } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { catchError, map, of, switchMap, tap } from 'rxjs';

import { FeaturePageData, FeaturePageItem, FeaturePageService, FeaturePageSource } from '../../services/feature-page.service';

@Component({
  selector: 'app-feature-page-detail',
  imports: [NgClass, RouterLink, MatButtonModule, MatCardModule, MatChipsModule, MatIconModule, MatProgressBarModule],
  templateUrl: './feature-page-detail.component.html',
  styleUrls: ['./feature-page.component.scss', './feature-page-detail.component.scss'],
})
export class FeaturePageDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly pages = inject(FeaturePageService);

  readonly page = signal<FeaturePageData | null>(null);
  readonly pageKey = signal('');
  readonly detailKey = signal('');
  readonly source = signal<FeaturePageSource>('feature-pages');
  readonly loading = signal(true);
  readonly error = signal('');
  readonly parentRoute = computed(() => this.routeForParent(this.source(), this.pageKey()));
  readonly parentLabel = computed(() => this.page()?.parentTitle || this.pageKey().replace(/-/g, ' '));

  private readonly featureRoutes: Record<string, string> = {
    triage: '/triage',
    evidence: '/evidence',
    runbooks: '/runbooks',
    postmortems: '/postmortems',
    'service-catalog': '/service-catalog',
    escalations: '/escalations',
    'model-monitoring': '/model-monitoring',
    'data-sources': '/data-sources',
    'audit-trail': '/audit-trail',
    settings: '/settings',
  };

  private readonly operationRoutes: Record<string, string> = {
    'service-health': '/services',
    deployments: '/deployments',
    'sla-monitor': '/sla-monitor',
    'alert-rules': '/alert-rules',
    'change-calendar': '/change-calendar',
    'on-call': '/on-call',
    'root-cause': '/root-cause',
  };

  constructor() {
    this.route.paramMap.pipe(
      map(params => ({
        source: this.normalizeSource(params.get('source')),
        pageKey: params.get('pageKey') ?? '',
        detailKey: params.get('detailKey') ?? '',
      })),
      tap(({ source, pageKey, detailKey }) => {
        this.source.set(source);
        this.pageKey.set(pageKey);
        this.detailKey.set(detailKey);
        this.loading.set(true);
        this.error.set('');
        this.page.set(null);
      }),
      switchMap(({ source, pageKey, detailKey }) =>
        this.pages.getSubpage(pageKey, detailKey, source).pipe(
          catchError(() => {
            this.error.set('This subpage data is unavailable or your role cannot access it.');
            return of(null);
          }),
        ),
      ),
      takeUntilDestroyed(),
    ).subscribe(page => {
      this.page.set(page);
      this.loading.set(false);
    });
  }

  stateClass(value?: string): string {
    return this.normalizedClass(value || 'neutral');
  }

  itemIcon(itemIcon?: string): string {
    return itemIcon || 'radio_button_checked';
  }

  itemRoute(item: FeaturePageItem): string | null {
    if (item.route) {
      return item.route;
    }
    const detailKey = item.detailKey || this.slugify(item.title);
    if (!detailKey || detailKey === this.detailKey()) {
      return null;
    }
    return `/content/${this.source()}/${this.pageKey()}/${detailKey}`;
  }

  compactKpiValue(value: string): boolean {
    return value.length > 6 && /[a-z]/i.test(value);
  }

  private normalizeSource(source: string | null): FeaturePageSource {
    return source === 'operations' ? 'operations' : 'feature-pages';
  }

  private routeForParent(source: FeaturePageSource, pageKey: string): string {
    return source === 'operations'
      ? this.operationRoutes[pageKey] || '/dashboard'
      : this.featureRoutes[pageKey] || '/dashboard';
  }

  private normalizedClass(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }

  private slugify(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'detail';
  }
}
