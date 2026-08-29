import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

import { OperationKpi, OperationListItem, OperationSideItem, OperationsDataService } from '../../../services/operations-data.service';

interface ChangeCalendarData {
  kpis: OperationKpi[];
  changes: OperationListItem[];
  controls: OperationSideItem[];
}

@Component({
  selector: 'app-change-calendar',
  imports: [MatCardModule, MatIconModule],
  templateUrl: './change-calendar.component.html',
  styleUrl: '../operations-page.scss',
})
export class ChangeCalendarComponent implements OnInit {
  private readonly dataService = inject(OperationsDataService);
  kpis: OperationKpi[] = [];
  changes: OperationListItem[] = [];
  controls: OperationSideItem[] = [];

  ngOnInit(): void {
    this.dataService.getPage<ChangeCalendarData>('change-calendar').subscribe(data => {
      this.kpis = data.kpis;
      this.changes = data.changes;
      this.controls = data.controls;
    });
  }
}
