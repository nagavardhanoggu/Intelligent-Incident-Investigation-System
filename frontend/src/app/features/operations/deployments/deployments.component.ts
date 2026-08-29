import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { OperationKpi, OperationListItem, OperationSideItem, OperationsDataService } from '../../../services/operations-data.service';

interface DeploymentsData {
  kpis: OperationKpi[];
  deployments: OperationListItem[];
  checkpoints: OperationSideItem[];
}

@Component({
  selector: 'app-deployments',
  imports: [MatCardModule, MatIconModule],
  templateUrl: './deployments.component.html',
  styleUrl: '../operations-page.scss',
})
export class DeploymentsComponent implements OnInit {
  private readonly dataService = inject(OperationsDataService);
  kpis: OperationKpi[] = [];
  deployments: OperationListItem[] = [];
  checkpoints: OperationSideItem[] = [];

  ngOnInit(): void {
    this.dataService.getPage<DeploymentsData>('deployments').subscribe(data => {
      this.kpis = data.kpis;
      this.deployments = data.deployments;
      this.checkpoints = data.checkpoints;
    });
  }
}
