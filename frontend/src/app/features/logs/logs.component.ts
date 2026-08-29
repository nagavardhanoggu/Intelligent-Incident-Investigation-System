import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MAT_DIALOG_DATA, MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { IncidentService } from '../../services/incident.service';

interface LogFile {
  id: number;
  incidentKey: string;
  fileName: string;
  format: string;
  uploadedAt: string;
  status: string;
  parsedContent: string | null;
}

interface ApiLog {
  id: number;
  incidentId: number;
  fileName: string;
  fileType: string;
  storagePath: string;
  uploadedAt: string;
  parsedContent: string | null;
}

@Component({
  selector: 'app-log-data-dialog',
  imports: [MatButtonModule, MatDialogModule, MatIconModule],
  template: `
    <section class="log-dialog-shell">
      <header class="log-dialog-header">
        <div>
          <span class="dialog-icon"><mat-icon>article</mat-icon></span>
          <div>
            <h2>{{ data.fileName }}</h2>
            <p>{{ data.incidentKey }} - {{ data.format }} - {{ data.uploadedAt }}</p>
          </div>
        </div>
        <button mat-icon-button mat-dialog-close type="button" aria-label="Close log data">
          <mat-icon>close</mat-icon>
        </button>
      </header>

      <mat-dialog-content class="log-dialog-content">
        <pre>{{ data.parsedContent || 'No parsed preview available for this log file.' }}</pre>
      </mat-dialog-content>

      <mat-dialog-actions align="end" class="log-dialog-actions">
        <button mat-flat-button mat-dialog-close type="button">Done</button>
      </mat-dialog-actions>
    </section>
  `,
  styles: [
    `
      .log-dialog-shell {
        display: grid;
        background: #ffffff;
      }

      .log-dialog-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        padding: 18px 20px;
        border-bottom: 1px solid #e4e7ec;
      }

      .log-dialog-header > div {
        display: grid;
        grid-template-columns: 42px minmax(0, 1fr);
        gap: 12px;
        min-width: 0;
      }

      .dialog-icon {
        display: grid;
        width: 42px;
        height: 42px;
        place-items: center;
        border-radius: 8px;
        background: #fff1eb;
        color: #f04b23;
      }

      h2,
      p {
        margin: 0;
      }

      h2 {
        overflow: hidden;
        color: #101828;
        font-size: 18px;
        line-height: 1.25;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      p {
        margin-top: 4px;
        color: #667085;
        font-size: 13px;
      }

      .log-dialog-content {
        padding: 16px 20px;
      }

      pre {
        max-height: 440px;
        margin: 0;
        padding: 14px;
        overflow: auto;
        border: 1px solid #e4e7ec;
        border-radius: 8px;
        background: #f8fafc;
        color: #17202a;
        font: 12px/1.55 Consolas, 'Courier New', monospace;
        white-space: pre-wrap;
      }

      .log-dialog-actions {
        min-height: 58px;
        padding: 10px 20px 16px;
        background: #ffffff;
      }

      .log-dialog-actions button {
        border-radius: 8px;
        background: #f04b23;
        color: #ffffff;
        font-weight: 700;
      }
    `,
  ],
})
export class LogDataDialogComponent {
  readonly data = inject<LogFile>(MAT_DIALOG_DATA);
}

@Component({
  selector: 'app-logs',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
    MatTableModule,
    MatTooltipModule,
  ],
  templateUrl: './logs.component.html',
  styleUrl: './logs.component.scss',
})
export class LogsComponent implements OnInit {
  @ViewChild('fileInput') private fileInput?: ElementRef<HTMLInputElement>;
  private readonly http = inject(HttpClient);
  private readonly dialog = inject(MatDialog);
  private readonly incidentService = inject(IncidentService);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  private logsLoaded = false;

  readonly columns = ['incidentKey', 'fileName', 'format', 'uploadedAt', 'status', 'actions'];
  incidents: { id: number; key: string }[] = [];
  logs: LogFile[] = [];
  readonly logRows = signal<LogFile[]>([]);
  readonly filters = signal({
    query: '',
    incidentKey: 'ALL',
    format: 'ALL',
    status: 'ALL',
  });
  readonly formatOptions = computed(() =>
    Array.from(new Set(this.logRows().map(log => log.format))).sort(),
  );
  readonly statusOptions = computed(() =>
    Array.from(new Set(this.logRows().map(log => log.status))).sort(),
  );
  readonly filteredLogs = computed(() => {
    const filters = this.filters();
    const query = filters.query.trim().toLowerCase();

    return this.logRows().filter(log => {
      const matchesQuery =
        !query ||
        `${log.incidentKey} ${log.fileName} ${log.format} ${log.status}`.toLowerCase().includes(query);
      const matchesIncident = filters.incidentKey === 'ALL' || log.incidentKey === filters.incidentKey;
      const matchesFormat = filters.format === 'ALL' || log.format === filters.format;
      const matchesStatus = filters.status === 'ALL' || log.status === filters.status;

      return matchesQuery && matchesIncident && matchesFormat && matchesStatus;
    });
  });
  selectedIncidentId = 0;
  selectedFile = signal<File | null>(null);
  lastUploadedLog = signal<LogFile | null>(null);
  uploadMessage = signal('');
  uploading = signal(false);

  ngOnInit(): void {
    this.incidentService.listIncidents().subscribe(incidents => {
      this.incidents = incidents.map(incident => ({ id: incident.id, key: incident.incidentKey }));
      if (!this.selectedIncidentId && this.incidents.length) {
        this.selectedIncidentId = this.incidents[0].id;
      }
      if (!this.logsLoaded && this.incidents.length) {
        this.logsLoaded = true;
        this.loadLogs();
      }
    });
  }

  openFilePicker(): void {
    this.fileInput?.nativeElement.click();
  }

  selectFile(event: Event): void {
    const [file] = Array.from((event.target as HTMLInputElement).files ?? []);
    this.uploadMessage.set('');
    this.selectedFile.set(file ?? null);
  }

  uploadLog(): void {
    const file = this.selectedFile();
    if (!file) {
      this.uploadMessage.set('Choose a TXT, LOG, or CSV file first.');
      return;
    }

    const extension = file.name.split('.').pop()?.toUpperCase() ?? '';
    if (!['TXT', 'LOG', 'CSV'].includes(extension)) {
      this.uploadMessage.set('Supported formats are TXT, LOG, and CSV.');
      return;
    }

    const formData = new FormData();
    formData.append('incident_id', String(this.selectedIncidentId));
    formData.append('file', file);
    this.uploading.set(true);
    this.uploadMessage.set('Uploading log file...');

    this.http.post<ApiLog>(`${this.apiUrl}/logs/upload`, formData).subscribe({
      next: result => {
        const uploadedLog = this.toRow(result);
        const nextLogs = [uploadedLog, ...this.logRows()];
        this.logs = nextLogs;
        this.logRows.set(nextLogs);
        this.lastUploadedLog.set(uploadedLog);
        this.selectedFile.set(null);
        if (this.fileInput) {
          this.fileInput.nativeElement.value = '';
        }
        this.uploadMessage.set('Log uploaded successfully.');
        this.uploading.set(false);
      },
      error: error => {
        this.uploadMessage.set(error?.error?.detail ?? 'Upload failed. Check backend and permissions.');
        this.uploading.set(false);
      },
    });
  }

  private loadLogs(): void {
    this.http.get<ApiLog[]>(`${this.apiUrl}/logs`).subscribe({
      next: logs => {
        const rows = logs.map(log => this.toRow(log));
        this.logs = rows;
        this.logRows.set(rows);
      },
      error: () => {
        this.uploadMessage.set('Could not load logs from the database.');
      },
    });
  }

  private toRow(log: ApiLog): LogFile {
    const incident = this.incidents.find(item => item.id === log.incidentId);
    return {
      id: log.id,
      incidentKey: incident?.key ?? `INC-${log.incidentId}`,
      fileName: log.fileName,
      format: log.fileType,
      uploadedAt: new Date(log.uploadedAt).toLocaleString(),
      status: 'Indexed',
      parsedContent: log.parsedContent,
    };
  }

  updateQuery(event: Event): void {
    this.filters.update(filters => ({
      ...filters,
      query: (event.target as HTMLInputElement).value,
    }));
  }

  updateIncidentFilter(incidentKey: string): void {
    this.filters.update(filters => ({ ...filters, incidentKey }));
  }

  updateFormatFilter(format: string): void {
    this.filters.update(filters => ({ ...filters, format }));
  }

  updateStatusFilter(status: string): void {
    this.filters.update(filters => ({ ...filters, status }));
  }

  clearFilters(): void {
    this.filters.set({
      query: '',
      incidentKey: 'ALL',
      format: 'ALL',
      status: 'ALL',
    });
  }

  viewLogData(log: LogFile): void {
    this.dialog.open(LogDataDialogComponent, {
      width: '820px',
      maxWidth: 'calc(100vw - 32px)',
      panelClass: 'log-data-dialog-panel',
      backdropClass: 'app-dialog-backdrop',
      autoFocus: false,
      restoreFocus: false,
      data: log,
    });
  }

  deleteLog(log: LogFile): void {
    this.http.delete(`${this.apiUrl}/logs/${log.id}`).subscribe({
      next: () => {
        const nextLogs = this.logRows().filter(item => item.id !== log.id);
        this.logs = nextLogs;
        this.logRows.set(nextLogs);
        if (this.lastUploadedLog()?.id === log.id) {
          this.lastUploadedLog.set(null);
        }
        this.uploadMessage.set(`${log.fileName} deleted.`);
      },
      error: error => {
        this.uploadMessage.set(error?.error?.detail ?? 'Delete failed. Check backend and permissions.');
      },
    });
  }
}
