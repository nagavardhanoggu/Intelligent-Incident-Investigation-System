import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { OperationKpi, OperationListItem, OperationSideItem, OperationsDataService } from '../../../services/operations-data.service';

interface ServiceHealthData {
  kpis: OperationKpi[];
  services: OperationListItem[];
  dependencies: OperationSideItem[];
}

@Component({
  selector: 'app-service-health',
  imports: [MatCardModule, MatIconModule],
  templateUrl: './service-health.component.html',
  styleUrl: '../operations-page.scss',
})
export class ServiceHealthComponent implements OnInit {
  private readonly dataService = inject(OperationsDataService);
  kpis: OperationKpi[] = [];
  services: OperationListItem[] = [];
  dependencies: OperationSideItem[] = [];

  ngOnInit(): void {
    this.dataService.getPage<ServiceHealthData>('service-health').subscribe(data => {
      this.kpis = data.kpis;
      this.services = data.services;
      this.dependencies = data.dependencies;
    });
  }
}
