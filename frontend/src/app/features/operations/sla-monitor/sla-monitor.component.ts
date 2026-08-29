import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { OperationKpi, OperationListItem, OperationSideItem, OperationsDataService } from '../../../services/operations-data.service';

interface SlaMonitorData {
  kpis: OperationKpi[];
  services: OperationListItem[];
  policies: OperationSideItem[];
}

@Component({
  selector: 'app-sla-monitor',
  imports: [MatCardModule, MatIconModule],
  templateUrl: './sla-monitor.component.html',
  styleUrl: '../operations-page.scss',
})
export class SlaMonitorComponent implements OnInit {
  private readonly dataService = inject(OperationsDataService);
  kpis: OperationKpi[] = [];
  services: OperationListItem[] = [];
  policies: OperationSideItem[] = [];

  ngOnInit(): void {
    this.dataService.getPage<SlaMonitorData>('sla-monitor').subscribe(data => {
      this.kpis = data.kpis;
      this.services = data.services;
      this.policies = data.policies;
    });
  }
}
