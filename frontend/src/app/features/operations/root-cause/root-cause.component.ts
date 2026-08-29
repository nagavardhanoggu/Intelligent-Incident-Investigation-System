import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { OperationKpi, OperationListItem, OperationSideItem, OperationsDataService } from '../../../services/operations-data.service';

interface RootCauseData {
  kpis: OperationKpi[];
  causes: OperationListItem[];
  recommendations: OperationSideItem[];
}

@Component({
  selector: 'app-root-cause',
  imports: [MatCardModule, MatIconModule],
  templateUrl: './root-cause.component.html',
  styleUrl: '../operations-page.scss',
})
export class RootCauseComponent implements OnInit {
  private readonly dataService = inject(OperationsDataService);
  kpis: OperationKpi[] = [];
  causes: OperationListItem[] = [];
  recommendations: OperationSideItem[] = [];

  ngOnInit(): void {
    this.dataService.getPage<RootCauseData>('root-cause').subscribe(data => {
      this.kpis = data.kpis;
      this.causes = data.causes;
      this.recommendations = data.recommendations;
    });
  }
}
