import { AsyncPipe, DatePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { catchError, forkJoin, map, of, switchMap } from 'rxjs';

import { InvestigationService, InvestigationWorkspace } from '../../../services/investigation.service';
import { ResolutionArticle, ResolutionService } from '../../../services/resolution.service';
import { SeverityChipComponent } from '../../../shared/components/severity-chip/severity-chip.component';

interface IncidentDetailsViewModel {
  workspace: InvestigationWorkspace;
  resolutions: ResolutionArticle[];
}

@Component({
  selector: 'app-incident-details',
  imports: [
    AsyncPipe,
    DatePipe,
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatProgressBarModule,
    SeverityChipComponent,
  ],
  templateUrl: './incident-details.component.html',
  styleUrl: './incident-details.component.scss',
})
export class IncidentDetailsComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly investigations = inject(InvestigationService);
  private readonly resolutions = inject(ResolutionService);

  readonly viewModel$ = this.route.paramMap.pipe(
    map(params => Number(params.get('id'))),
    switchMap(id =>
      forkJoin({
        workspace: this.investigations.getWorkspace(id),
        resolutions: this.resolutions.list().pipe(
          map(items => items.filter(item => item.incidentId === id)),
        ),
      }),
    ),
    catchError(() => of(null)),
  );

  impactSummary(workspace: InvestigationWorkspace) {
    return [
      { label: 'Operational Risk', value: workspace.summary.riskLevel, icon: 'warning', note: workspace.incident.priority },
      { label: 'Signals', value: String(workspace.summary.signalCount), icon: 'monitoring', note: 'Stored evidence records' },
      { label: 'Logs', value: String(workspace.summary.logCount), icon: 'article', note: 'Uploaded log files' },
      { label: 'Similar Incidents', value: String(workspace.similarIncidentKeys.length), icon: 'travel_explore', note: 'Matching priority' },
    ];
  }

  evidenceLogs(workspace: InvestigationWorkspace): string[] {
    return workspace.logs
      .flatMap(log => (log.parsedContent ?? '').split(/\r?\n/))
      .filter(line => line.trim().length > 0)
      .slice(0, 8);
  }
}
