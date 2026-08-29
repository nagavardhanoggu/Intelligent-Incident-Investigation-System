import { AfterViewInit, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { IncidentCreateDialogComponent } from './incident-create-dialog.component';
import { IncidentService } from '../../../services/incident.service';

@Component({
  selector: 'app-create-incident',
  imports: [MatButtonModule, MatCardModule, MatDialogModule],
  templateUrl: './create-incident.component.html',
  styleUrl: './create-incident.component.scss',
})
export class CreateIncidentComponent implements AfterViewInit {
  private readonly dialog = inject(MatDialog);
  private readonly router = inject(Router);
  private readonly incidentService = inject(IncidentService);
  private opened = false;

  ngAfterViewInit(): void {
    queueMicrotask(() => this.openCreateDialog());
  }

  openCreateDialog(): void {
    if (this.opened) {
      return;
    }

    this.opened = true;
    const dialogRef = this.dialog.open(IncidentCreateDialogComponent, {
      width: '720px',
      maxWidth: 'calc(100vw - 32px)',
      panelClass: 'incident-create-dialog-panel',
      backdropClass: 'app-dialog-backdrop',
      autoFocus: false,
      restoreFocus: false,
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result?.mode === 'create') {
        this.incidentService.createIncident(result.value);
      }

      this.router.navigate(['/incidents']);
    });
  }
}
