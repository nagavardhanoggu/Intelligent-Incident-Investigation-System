import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

import { Incident } from '../../../models/incident.model';
import { IncidentService } from '../../../services/incident.service';
import { SeverityChipComponent } from '../../../shared/components/severity-chip/severity-chip.component';

@Component({
  selector: 'app-investigation-landing',
  imports: [
    DatePipe,
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    SeverityChipComponent,
  ],
  templateUrl: './investigation-landing.component.html',
  styleUrl: './investigation-landing.component.scss',
})
export class InvestigationLandingComponent {
  private readonly incidentService = inject(IncidentService);
  private readonly incidents = toSignal(this.incidentService.listIncidents(), { initialValue: [] });

  readonly searchQuery = signal('');
  readonly summary = computed(() => {
    const incidents = this.incidents();

    return [
      {
        label: 'Available incidents',
        value: incidents.length,
        icon: 'folder_open',
      },
      {
        label: 'Active investigations',
        value: incidents.filter(incident => incident.status === 'INVESTIGATING').length,
        icon: 'manage_search',
      },
      {
        label: 'Critical priority',
        value: incidents.filter(incident => incident.priority === 'CRITICAL').length,
        icon: 'priority_high',
      },
    ];
  });

  readonly filteredIncidents = computed(() => {
    const query = this.searchQuery().trim().toLowerCase();

    return [...this.incidents()]
      .filter(incident =>
        !query ||
        [incident.incidentKey, incident.title, incident.description, incident.assignedUser, incident.status]
          .join(' ')
          .toLowerCase()
          .includes(query),
      )
      .sort((first, second) => this.sortScore(second) - this.sortScore(first));
  });

  updateSearch(event: Event): void {
    this.searchQuery.set((event.target as HTMLInputElement).value);
  }

  clearSearch(): void {
    this.searchQuery.set('');
  }

  private sortScore(incident: Incident): number {
    const priorityWeight: Record<Incident['priority'], number> = {
      CRITICAL: 4,
      HIGH: 3,
      MEDIUM: 2,
      LOW: 1,
    };

    const activeWeight = incident.status === 'INVESTIGATING' ? 10 : incident.status === 'OPEN' ? 5 : 0;
    return activeWeight + priorityWeight[incident.priority];
  }
}
