import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { OperationKpi, OperationListItem, OperationSideItem, OperationsDataService } from '../../../services/operations-data.service';

interface AlertRulesData {
  kpis: OperationKpi[];
  rules: OperationListItem[];
  routing: OperationSideItem[];
}

@Component({
  selector: 'app-alert-rules',
  imports: [MatCardModule, MatIconModule],
  templateUrl: './alert-rules.component.html',
  styleUrl: '../operations-page.scss',
})
export class AlertRulesComponent implements OnInit {
  private readonly dataService = inject(OperationsDataService);
  kpis: OperationKpi[] = [];
  rules: OperationListItem[] = [];
  routing: OperationSideItem[] = [];

  ngOnInit(): void {
    this.dataService.getPage<AlertRulesData>('alert-rules').subscribe(data => {
      this.kpis = data.kpis;
      this.rules = data.rules;
      this.routing = data.routing;
    });
  }
}
