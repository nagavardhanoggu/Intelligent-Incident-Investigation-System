import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { finalize } from 'rxjs';

import { ResolutionArticle, ResolutionService } from '../../services/resolution.service';

@Component({
  selector: 'app-knowledge-base',
  imports: [
    MatButtonModule,
    MatCardModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
  ],
  templateUrl: './knowledge-base.component.html',
  styleUrl: './knowledge-base.component.scss',
})
export class KnowledgeBaseComponent implements OnInit {
  private readonly resolutionService = inject(ResolutionService);

  readonly searchQuery = signal('');
  readonly articles = signal<ResolutionArticle[]>([]);
  readonly loading = signal(true);
  readonly error = signal('');

  readonly summary = computed(() => {
    const articles = this.articles();
    const rootCauses = new Set(articles.map(article => article.rootCause));
    const incidents = new Set(articles.map(article => article.incidentId));

    return [
      { label: 'Resolution Articles', value: String(articles.length), icon: 'article' },
      { label: 'Root Causes', value: String(rootCauses.size), icon: 'account_tree' },
      { label: 'Incidents Covered', value: String(incidents.size), icon: 'task_alt' },
      {
        label: 'Latest Update',
        value: articles.length ? this.formatUpdatedAt(articles[0].updatedAt) : '-',
        icon: 'update',
      },
    ];
  });

  readonly searchTags = computed(() => [
    ...new Set(this.articles().map(article => article.rootCause)),
  ]);

  readonly recentArticles = computed(() => this.articles().slice(0, 4));

  readonly filteredArticles = computed(() => {
    const query = this.searchQuery().trim().toLowerCase();

    if (!query) {
      return this.articles();
    }

    return this.articles().filter(article =>
      [
        article.id,
        article.incidentId,
        article.incidentTitle,
        article.rootCause,
        article.resolution,
        article.preventionSteps,
      ]
        .filter(value => value !== null)
        .join(' ')
        .toLowerCase()
        .includes(query),
    );
  });

  ngOnInit(): void {
    this.loadArticles();
  }

  loadArticles(): void {
    this.loading.set(true);
    this.error.set('');

    this.resolutionService
      .list()
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: articles => this.articles.set(articles),
        error: () => {
          this.articles.set([]);
          this.error.set('Unable to load resolution articles from the database.');
        },
      });
  }

  updateSearch(event: Event): void {
    this.searchQuery.set((event.target as HTMLInputElement).value);
  }

  applySearchTag(tag: string): void {
    this.searchQuery.set(tag);
  }

  findArticle(article: ResolutionArticle): void {
    this.searchQuery.set(String(article.incidentId));
  }

  clearSearch(): void {
    this.searchQuery.set('');
  }

  formatUpdatedAt(value: string): string {
    const date = new Date(value);
    return Number.isNaN(date.getTime())
      ? value
      : new Intl.DateTimeFormat('en', { dateStyle: 'medium' }).format(date);
  }
}
