import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { OperationKpi, OperationListItem, OperationSideItem, OperationsDataService } from '../../../services/operations-data.service';

interface OnCallData {
  kpis: OperationKpi[];
  responders: OperationListItem[];
  runbook: OperationSideItem[];
}

@Component({
  selector: 'app-on-call',
  imports: [MatCardModule, MatIconModule],
  templateUrl: './on-call.component.html',
  styleUrl: '../operations-page.scss',
})
export class OnCallComponent implements OnInit {
  private readonly dataService = inject(OperationsDataService);
  kpis: OperationKpi[] = [];
  responders: OperationListItem[] = [];
  runbook: OperationSideItem[] = [];

  ngOnInit(): void {
    this.dataService.getPage<OnCallData>('on-call').subscribe(data => {
      this.kpis = data.kpis;
      this.responders = data.responders;
      this.runbook = data.runbook;
    });
  }
}
