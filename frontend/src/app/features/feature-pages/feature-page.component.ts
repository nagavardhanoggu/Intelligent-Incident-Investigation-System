import { NgClass } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { catchError, map, of, switchMap, tap } from 'rxjs';

import { FeaturePageData, FeaturePageService } from '../../services/feature-page.service';

@Component({
  selector: 'app-feature-page',
  imports: [NgClass, RouterLink, MatButtonModule, MatCardModule, MatChipsModule, MatIconModule, MatProgressBarModule],
  templateUrl: './feature-page.component.html',
  styleUrl: './feature-page.component.scss',
})
export class FeaturePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly pages = inject(FeaturePageService);

  readonly page = signal<FeaturePageData | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');

  constructor() {
    this.route.data.pipe(
      map(data => String(data['pageKey'] ?? '')),
      tap(() => {
        this.loading.set(true);
        this.error.set('');
        this.page.set(null);
      }),
      switchMap(pageKey =>
        this.pages.getPage(pageKey).pipe(
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

  private normalizedClass(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }
}
