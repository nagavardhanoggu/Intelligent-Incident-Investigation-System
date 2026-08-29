# Intelligent Incident Investigation System - Application Flow

## Purpose

The Intelligent Incident Investigation System helps DevOps, SRE, Production Support, and IT Operations teams investigate production incidents by combining incident records, logs, metrics, timelines, ML predictions, and resolution knowledge.

## Login

Users sign in through the login page using database-backed credentials. FastAPI validates the email and password against MySQL, returns a JWT token, and sends the user's roles and permissions to Angular.

### Seeded Credentials

| Role | Email | Password |
| --- | --- | --- |
| Admin | admin@example.com | password |
| Investigator | investigator@example.com | password |
| Viewer | viewer@example.com | password |

## Role-Based Access

| Page / Feature | Admin | Investigator | Viewer |
| --- | --- | --- | --- |
| Dashboard | View | View | View |
| Incidents | Create, View, Edit, Delete | Create, View, Edit | View |
| Investigation Workspace | View, Investigate | View, Investigate | View only if permitted |
| Logs | View, Upload | View, Upload | View only |
| Metrics | View | View | View |
| ML Prediction | Run, View | Run, View | View only |
| Knowledge Base | Manage | Add/View | View |
| Reports | View | View | View |
| Users | Create, Edit, Delete | No access | No access |

## Main Pages

### Dashboard

The dashboard gives a high-level operational summary.

It shows:
- Total incidents
- Open incidents
- Closed incidents
- Critical incidents
- Average MTTR
- SLA breaches
- Reopened incidents
- Prediction volume
- Incident trends
- Root cause distribution
- Active investigation queue
- Recommended actions

### Incidents

The incidents page is the main incident directory.

It is used to:
- View incident records
- Open incident details
- Create new incidents
- Edit incidents
- Delete incidents as Admin

The action column is permission-based:
- Admin: Open, Edit, Delete
- Investigator: Open, Edit
- Viewer: Open only

### Create / Edit Incident

The incident modal captures:
- Incident title
- Description
- Priority
- Impact
- Urgency
- Assigned investigator

Create mode saves a new incident. Edit mode updates an existing incident.

### Investigation Workspace

The investigation workspace is used during active incident triage.

It displays:
- Incident summary
- Risk level
- Signal counts
- Timeline events
- Metrics
- Uploaded logs
- ML prediction
- Decision factors
- Recommended actions
- Similar incidents

Data is loaded from the backend using:

```http
GET /api/v1/investigations/{incident_id}
```

### Logs

The logs page is used to attach technical evidence to incidents.

Supported formats:
- TXT
- LOG
- CSV

Flow:
1. Select an incident.
2. Choose a log file.
3. Upload the file.
4. Backend stores metadata and parsed preview in MySQL.
5. Investigation workspace displays uploaded log evidence.

### Metrics

The metrics page displays system health signals such as:
- CPU usage
- Memory usage
- Disk usage
- Response time
- Error rate
- Database connections

These metrics help correlate abnormal behavior with incident timelines.

### ML Training / Incident Prediction

The ML page lets an investigator enter incident attributes and run root cause prediction.

Inputs include:
- Priority
- Impact
- Urgency
- Reassignment count
- Reopen count
- SLA status
- Category
- Subcategory
- Symptom
- Assignment group
- Contact type
- Knowledge used
- System modification count

The backend uses a Scikit-Learn Decision Tree model and returns:
- Predicted root cause
- Confidence score
- Top probable causes
- Key decision factors
- Recommended actions
- Model version

### Knowledge Base

The knowledge base stores verified resolution articles.

It is used to:
- Search known fixes
- Review root causes
- Review prevention steps
- Reuse previous incident resolutions
- Suggest similar incidents

### Reports

Reports provide operational analytics:
- Monthly incident trends
- SLA health
- MTTR
- Root cause distribution
- Team workload
- Incident closure performance

### User Management

The user management page is available only to Admin users.

Admin can:
- Create users
- Edit users
- Delete users
- Assign roles
- Activate or deactivate accounts

## End-To-End Incident Flow

```text
User Login
  ↓
JWT Token + Permissions Loaded
  ↓
Dashboard Opens
  ↓
Incident Created or Selected
  ↓
Logs Uploaded
  ↓
Metrics Reviewed
  ↓
Timeline Generated
  ↓
ML Prediction Runs
  ↓
Root Cause Reviewed
  ↓
Recommended Actions Followed
  ↓
Resolution Added
  ↓
Knowledge Base Updated
  ↓
Reports Reflect Incident Outcome
```

## Backend Flow

```text
Angular Request
  ↓
JWT Interceptor Adds Token
  ↓
FastAPI Authenticates User
  ↓
Permission Guard Validates Access
  ↓
Repository / Service Reads MySQL
  ↓
Business Logic or ML Service Runs
  ↓
Response Returned to Angular
```

## ML Prediction Flow

```text
Incident Features
  ↓
FastAPI /predict Endpoint
  ↓
Feature Encoding
  ↓
Decision Tree Classifier
  ↓
Root Cause Prediction
  ↓
Confidence Score
  ↓
Prediction Stored in MySQL
  ↓
Result Displayed in Angular
```

## Production Notes

- Permissions must be enforced in both Angular and FastAPI.
- Angular should hide actions that the user cannot perform.
- FastAPI must still reject unauthorized requests.
- Passwords are hashed before storage.
- JWT tokens should be short-lived.
- Incident, user, prediction, and resolution changes should be audit logged.
- The ML model should be retrained periodically with verified historical incident data.
