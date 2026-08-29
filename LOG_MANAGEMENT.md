# Log Management Module

## Purpose

The Log Management module allows investigators to upload operational log evidence for a production incident. Logs are linked to incidents and can be reviewed later inside the Investigation Workspace.

## Supported File Types

- TXT
- LOG
- CSV

## User Flow

```text
Open Log Management Page
  ↓
Select Incident
  ↓
Choose TXT / LOG / CSV File
  ↓
Upload Log
  ↓
FastAPI Validates File and Permission
  ↓
File Stored on Server
  ↓
Log Metadata Saved in MySQL
  ↓
Log Appears in Log Table
  ↓
Investigation Workspace Shows Log Evidence
```

## Frontend Page

Route:

```text
http://localhost:4200/logs
```

Main UI sections:

- Page title and subtitle
- Upload Incident Log card
- Incident dropdown
- Choose File button
- Upload Log button
- Upload success/error message
- Uploaded logs table
- Empty state when no logs are available

## Upload Validation

Frontend validates:

- A file must be selected
- File extension must be TXT, LOG, or CSV
- Upload button is disabled while upload is in progress

Backend validates:

- User must have `logs:upload` permission
- Incident ID must exist
- File extension must be TXT, LOG, or CSV
- File content is read and stored safely

## Role Access

| Role | View Logs | Upload Logs |
| --- | --- | --- |
| Admin | Yes | Yes, if permission assigned |
| Investigator | Yes | Yes |
| Viewer | Yes | No |

## Backend APIs

### Upload Log

```http
POST /api/v1/logs/upload
```

Request type:

```text
multipart/form-data
```

Fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| incident_id | number | Yes | Incident ID |
| file | file | Yes | TXT, LOG, or CSV file |

Response:

```json
{
  "id": 1,
  "incidentId": 101,
  "fileName": "checkout-errors.log",
  "fileType": "LOG",
  "storagePath": "uploads/101-checkout-errors.log",
  "uploadedAt": "2026-08-25T10:30:00"
}
```

### List All Logs

```http
GET /api/v1/logs
```

Returns all uploaded log metadata.

### Get Logs By Incident

```http
GET /api/v1/logs/{incident_id}
```

Returns logs linked to one incident.

## Database Table

Table:

```text
logs
```

Columns:

| Column | Type | Description |
| --- | --- | --- |
| id | INT | Primary key |
| incident_id | INT | Foreign key to incidents |
| file_name | VARCHAR(255) | Uploaded file name |
| file_type | VARCHAR(20) | TXT, LOG, or CSV |
| storage_path | VARCHAR(500) | Stored file path |
| parsed_content | TEXT | Parsed log preview |
| uploaded_at | DATETIME | Upload timestamp |

Relationship:

```text
incidents.id 1 ─── many logs.incident_id
```

## MySQL Schema

```sql
CREATE TABLE logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  incident_id INT NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(20) NOT NULL,
  storage_path VARCHAR(500) NOT NULL,
  parsed_content TEXT NULL,
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_logs_incident_id (incident_id),
  CONSTRAINT fk_logs_incident
    FOREIGN KEY (incident_id)
    REFERENCES incidents(id)
);
```

## Angular Integration

Component:

```text
frontend/src/app/features/logs/logs.component.ts
```

Responsibilities:

- Load existing logs from backend
- Store selected incident ID
- Store selected file
- Validate file extension
- Submit `FormData` to FastAPI
- Show success or error message
- Refresh uploaded log table

## FastAPI Integration

Router:

```text
backend/app/routers/log_router.py
```

Responsibilities:

- Validate permissions
- Validate incident exists
- Validate file type
- Save file to upload directory
- Store metadata in MySQL
- Store parsed preview content
- Return upload response

## Investigation Workspace Integration

Uploaded logs are displayed in:

```text
http://localhost:4200/investigation/101
```

The investigation API returns logs from MySQL:

```http
GET /api/v1/investigations/{incident_id}
```

The workspace shows:

- File name
- File type
- Upload time
- Parsed log preview

## Error States

Common errors:

| Error | Meaning | Fix |
| --- | --- | --- |
| Choose a TXT, LOG, or CSV file first | No file selected | Select a file |
| Supported formats are TXT, LOG, and CSV | Invalid extension | Upload valid file |
| Incident not found | Invalid incident ID | Select existing incident |
| Upload failed | Backend/API issue | Check backend and token |
| Could not load logs from the database | Database/API unavailable | Restart backend or check MySQL |

## Security Notes

- Never allow unrestricted file types.
- Store uploaded files outside frontend public assets.
- Limit max upload file size in production.
- Scan uploaded files if used in enterprise environments.
- Do not execute uploaded log content.
- Keep parsed previews text-only.
- Require JWT authentication for every log endpoint.
- Enforce `logs:view` and `logs:upload` permissions in FastAPI.
