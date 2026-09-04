import { NgClass } from '@angular/common';
import { Component, HostBinding, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { catchError, map, of, switchMap, tap } from 'rxjs';

import { FeaturePageData, FeaturePageService, FeaturePageSource } from '../../services/feature-page.service';

@Component({
  selector: 'app-feature-page',
  imports: [NgClass, RouterLink, MatButtonModule, MatCardModule, MatChipsModule, MatIconModule, MatProgressBarModule],
  templateUrl: './feature-page.component.html',
  styleUrl: './feature-page.component.scss',
})
export class FeaturePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly pages = inject(FeaturePageService);

  @HostBinding('class.triage-page')
  get isTriagePage(): boolean {
    return this.pageKey() === 'triage';
  }

  @HostBinding('class.evidence-page')
  get isEvidencePage(): boolean {
    return this.pageKey() === 'evidence';
  }

  readonly page = signal<FeaturePageData | null>(null);
  readonly pageKey = signal('');
  readonly source = signal<FeaturePageSource>('feature-pages');
  readonly loading = signal(true);
  readonly error = signal('');

  constructor() {
    this.route.data.pipe(
      map(data => ({
        pageKey: String(data['pageKey'] ?? ''),
        source: (data['pageSource'] ?? 'feature-pages') as FeaturePageSource,
      })),
      tap(({ pageKey, source }) => {
        this.pageKey.set(pageKey);
        this.source.set(source);
        this.loading.set(true);
        this.error.set('');
        this.page.set(null);
      }),
      switchMap(({ pageKey, source }) =>
        this.pages.getPage(pageKey, source).pipe(
          catchError(() => {
            this.error.set('This page data is unavailable or your role cannot access it.');
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

  itemRoute(item: { title: string; route?: string; detailKey?: string }): string | null {
    if (item.route) {
      return item.route;
    }
    const pageKey = this.pageKey();
    const detailKey = item.detailKey || this.slugify(item.title);
    return pageKey && detailKey ? `/content/${this.source()}/${pageKey}/${detailKey}` : null;
  }

  compactKpiValue(value: string): boolean {
    return value.length > 6 && /[a-z]/i.test(value);
  }

  private normalizedClass(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }

  private slugify(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'detail';
  }
}
