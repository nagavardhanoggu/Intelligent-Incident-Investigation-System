FEATURE_PAGE_PERMISSIONS = {
    "triage": "triage:view",
    "evidence": "evidence:view",
    "runbooks": "runbooks:view",
    "postmortems": "postmortems:view",
    "service-catalog": "service_catalog:view",
    "escalations": "escalations:view",
    "model-monitoring": "model_monitoring:view",
    "data-sources": "data_sources:view",
    "audit-trail": "audit_trail:view",
    "settings": "settings:view",
}


DEFAULT_FEATURE_PAGES = {
    "triage": {
        "title": "Triage Board",
        "subtitle": "Prioritize new incidents, assess operational risk, and assign investigation ownership.",
        "pill": {"icon": "fact_check", "label": "Live intake"},
        "kpis": [
            {"label": "P1 / Critical", "value": "3", "helper": "Immediate review required", "icon": "priority_high", "state": "critical"},
            {"label": "SLA At Risk", "value": "5", "helper": "Needs owner confirmation", "icon": "timer", "state": "warning"},
            {"label": "Unassigned", "value": "2", "helper": "Waiting for dispatch", "icon": "person_search", "state": "warning"},
            {"label": "Ready To Close", "value": "4", "helper": "Pending validation notes", "icon": "task_alt", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Priority Intake",
                "caption": "Open incidents ranked by severity and SLA pressure",
                "items": [
                    {
                        "title": "INC-2026-000101",
                        "subtitle": "Checkout latency spike",
                        "detail": "Payment gateway latency crossed P95 threshold after deployment.",
                        "meta": "Owner: Investigator User",
                        "status": "Critical",
                        "icon": "report_problem",
                        "progress": 82,
                        "tags": ["P1", "Checkout", "SLA risk"],
                        "route": "/incidents/101",
                    },
                    {
                        "title": "INC-2026-000102",
                        "subtitle": "Database connection saturation",
                        "detail": "API workers exhausted the primary database connection pool.",
                        "meta": "Owner: Investigator User",
                        "status": "High",
                        "icon": "storage",
                        "progress": 68,
                        "tags": ["P2", "Database", "Pool"],
                        "route": "/incidents/102",
                    },
                    {
                        "title": "INC-2026-000111",
                        "subtitle": "Authentication error spike",
                        "detail": "Identity release caused signing-key cache mismatch across login nodes.",
                        "meta": "Owner: Identity squad",
                        "status": "Critical",
                        "icon": "verified_user",
                        "progress": 74,
                        "tags": ["Auth", "Deployment"],
                        "route": "/incidents/111",
                    },
                ],
            },
            {
                "title": "Triage Decisions",
                "caption": "Current routing and response actions",
                "items": [
                    {"title": "Assign database specialist", "detail": "INC-2026-000102 requires pool telemetry and query wait analysis.", "status": "Active", "icon": "person_add", "tags": ["Database"]},
                    {"title": "Escalate checkout incident", "detail": "Payment path remains customer-facing and needs incident commander review.", "status": "Escalated", "icon": "outbound", "tags": ["P1"]},
                    {"title": "Validate closure evidence", "detail": "Resolved memory and cache incidents need post-fix metric windows attached.", "status": "Pending", "icon": "rule", "tags": ["Review"]},
                ],
            },
        ],
    },
    "evidence": {
        "title": "Evidence Center",
        "subtitle": "Review logs, metrics, predictions, timeline events, and uploaded artifacts in one investigation view.",
        "pill": {"icon": "folder_copy", "label": "Evidence indexed"},
        "kpis": [
            {"label": "Log Files", "value": "32", "helper": "Parsed and searchable", "icon": "article", "state": "healthy"},
            {"label": "Metric Windows", "value": "84", "helper": "Linked to incidents", "icon": "monitoring", "state": "healthy"},
            {"label": "ML Predictions", "value": "15", "helper": "Saved model outputs", "icon": "psychology", "state": "healthy"},
            {"label": "Missing Evidence", "value": "3", "helper": "Need upload follow-up", "icon": "plagiarism", "state": "warning"},
        ],
        "sections": [
            {
                "title": "Recent Evidence Packages",
                "caption": "Artifacts grouped by incident",
                "items": [
                    {"title": "Checkout latency spike", "subtitle": "INC-2026-000101", "detail": "3 log files, 5 metric windows, 1 root-cause prediction, 6 timeline events.", "meta": "Last indexed: Aug 26, 2026 2:17 PM", "status": "Complete", "icon": "inventory_2", "tags": ["Logs", "Metrics", "Prediction"], "route": "/incidents/101"},
                    {"title": "Database connection saturation", "subtitle": "INC-2026-000102", "detail": "Connection pool logs, APM metrics, mitigation events, and recovery validation.", "meta": "Last indexed: Aug 26, 2026 8:59 AM", "status": "Complete", "icon": "storage", "tags": ["Database", "APM"], "route": "/incidents/102"},
                    {"title": "Authentication error spike", "subtitle": "INC-2026-000111", "detail": "Identity APM traces and deployment rollback notes attached.", "meta": "Last indexed: Jun 18, 2026 12:38 PM", "status": "Needs review", "icon": "security", "tags": ["Auth", "Release"], "route": "/incidents/111"},
                ],
            },
            {
                "title": "Evidence Gaps",
                "caption": "Follow-up items before closure",
                "items": [
                    {"title": "Attach post-mitigation CPU window", "detail": "Checkout service needs 30 minutes of stable CPU and latency data.", "status": "Open", "icon": "show_chart", "tags": ["Metrics"]},
                    {"title": "Upload resolver traces", "detail": "DNS incident should include failed lookup samples from both affected zones.", "status": "Open", "icon": "dns", "tags": ["Network"]},
                    {"title": "Confirm dead-letter replay output", "detail": "Order event consumer requires replay count and failed-event quarantine evidence.", "status": "Pending", "icon": "fact_check", "tags": ["Kafka"]},
                ],
            },
        ],
    },
    "runbooks": {
        "title": "Runbooks",
        "subtitle": "Use repeatable recovery procedures for common incident root causes and service failures.",
        "pill": {"icon": "menu_book", "label": "Validated actions"},
        "kpis": [
            {"label": "Published", "value": "12", "helper": "Ready for incident use", "icon": "library_books", "state": "healthy"},
            {"label": "Needs Review", "value": "3", "helper": "Ownership or command drift", "icon": "rate_review", "state": "warning"},
            {"label": "Linked Incidents", "value": "15", "helper": "Resolved examples attached", "icon": "device_hub", "state": "healthy"},
            {"label": "Automation", "value": "6", "helper": "Scripts or checks available", "icon": "terminal", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Operational Runbooks",
                "caption": "Primary procedures for investigators",
                "items": [
                    {"title": "Database Connection Pool Saturation", "subtitle": "Database Issue", "detail": "Check active connections, waiting requests, pool max, slow queries, and recycle stale workers.", "meta": "Owner: Database Platform", "status": "Published", "icon": "storage", "tags": ["DB", "Pool", "High impact"]},
                    {"title": "Deployment Rollback Validation", "subtitle": "Deployment Failure", "detail": "Identify release artifact, rollback policy, dependent migrations, and post-rollback metric checks.", "meta": "Owner: Release Engineering", "status": "Published", "icon": "rocket_launch", "tags": ["CI/CD", "Rollback"]},
                    {"title": "Memory Leak Stabilization", "subtitle": "Memory Leak", "detail": "Capture heap profile, disable unbounded cache path, restart affected pods, and monitor GC pause time.", "meta": "Owner: Runtime Platform", "status": "Published", "icon": "memory", "tags": ["Heap", "GC"]},
                    {"title": "DNS Failure Containment", "subtitle": "Network Issue", "detail": "Verify resolver health, policy changes, packet loss, cache refresh, and affected service discovery paths.", "meta": "Owner: Network Operations", "status": "Review", "icon": "dns", "tags": ["DNS", "Network"]},
                ],
            },
            {
                "title": "Approval Checklist",
                "caption": "Before using an action in production",
                "items": [
                    {"title": "Confirm blast radius", "detail": "Validate affected services, zones, tenants, and customer workflows.", "status": "Required", "icon": "hub"},
                    {"title": "Record evidence links", "detail": "Attach logs, metrics, prediction output, and timeline markers before closure.", "status": "Required", "icon": "attach_file"},
                    {"title": "Update prevention step", "detail": "Every reused runbook should produce one preventive control or alert change.", "status": "Required", "icon": "task_alt"},
                ],
            },
        ],
    },
    "postmortems": {
        "title": "Postmortems",
        "subtitle": "Review closed incidents, root causes, customer impact, and prevention commitments.",
        "pill": {"icon": "history_edu", "label": "Review ready"},
        "kpis": [
            {"label": "Completed", "value": "8", "helper": "Closed with action items", "icon": "task_alt", "state": "healthy"},
            {"label": "Drafts", "value": "4", "helper": "Need reviewer sign-off", "icon": "edit_note", "state": "warning"},
            {"label": "Open Actions", "value": "11", "helper": "Preventive controls pending", "icon": "assignment_late", "state": "warning"},
            {"label": "Repeat Causes", "value": "3", "helper": "Seen more than once", "icon": "repeat", "state": "critical"},
        ],
        "sections": [
            {
                "title": "Recent Reviews",
                "caption": "Closed incidents requiring learning capture",
                "items": [
                    {"title": "Reporting worker memory growth", "subtitle": "INC-2026-000115", "detail": "Export pipeline retained page buffers instead of streaming them to storage.", "meta": "Root cause: Memory Leak", "status": "Draft", "icon": "description", "tags": ["Memory", "Exports"], "route": "/incidents/115"},
                    {"title": "Checkout pod readiness failures", "subtitle": "INC-2026-000113", "detail": "Deployment configuration referenced an obsolete readiness endpoint.", "meta": "Root cause: Deployment Failure", "status": "Complete", "icon": "description", "tags": ["Deployment"], "route": "/incidents/113"},
                    {"title": "Primary database replica lag", "subtitle": "INC-2026-000110", "detail": "Reporting traffic was routed to a transactional replica without workload limits.", "meta": "Root cause: Database Issue", "status": "Action open", "icon": "description", "tags": ["Database"], "route": "/incidents/110"},
                ],
            },
            {
                "title": "Prevention Commitments",
                "caption": "Controls created by postmortem review",
                "items": [
                    {"title": "Streaming export guardrail", "detail": "Large exports must use bounded memory streaming with heap-growth alerts.", "status": "In progress", "icon": "rule"},
                    {"title": "Readiness probe validation", "detail": "Release pipeline blocks deploys when probe paths are missing from the artifact.", "status": "Complete", "icon": "verified"},
                    {"title": "Replica workload routing", "detail": "Reporting queries now require analytics replica routing labels.", "status": "In progress", "icon": "route"},
                ],
            },
        ],
    },
    "service-catalog": {
        "title": "Service Catalog",
        "subtitle": "Track service ownership, criticality, dependencies, and incident relationships.",
        "pill": {"icon": "apps", "label": "Production catalog"},
        "kpis": [
            {"label": "Tier 1 Services", "value": "7", "helper": "Customer critical paths", "icon": "workspace_premium", "state": "critical"},
            {"label": "Owners Mapped", "value": "94%", "helper": "Primary and backup owner", "icon": "groups", "state": "healthy"},
            {"label": "Dependency Gaps", "value": "5", "helper": "Need review", "icon": "account_tree", "state": "warning"},
            {"label": "Recent Incidents", "value": "15", "helper": "Linked by service", "icon": "report_problem", "state": "warning"},
        ],
        "sections": [
            {
                "title": "Critical Services",
                "caption": "Ownership and risk state",
                "items": [
                    {"title": "Checkout Service", "subtitle": "Tier 1", "detail": "Owns checkout orchestration, payment gateway routing, and order confirmation handoff.", "meta": "Owner: Commerce Platform", "status": "At risk", "icon": "shopping_cart", "tags": ["Payments", "Orders"], "route": "/services"},
                    {"title": "Identity Service", "subtitle": "Tier 1", "detail": "Authentication, signing-key rotation, session validation, and access token issuance.", "meta": "Owner: Identity Platform", "status": "Watch", "icon": "verified_user", "tags": ["Auth", "Security"], "route": "/services"},
                    {"title": "Primary Database", "subtitle": "Tier 1", "detail": "Transactional order, inventory, and customer state with replica routing dependencies.", "meta": "Owner: Database Platform", "status": "Healthy", "icon": "storage", "tags": ["MySQL", "Replica"], "route": "/services"},
                    {"title": "Notification Service", "subtitle": "Tier 2", "detail": "Transactional email, customer campaign events, and incident alert delivery.", "meta": "Owner: Messaging Platform", "status": "Healthy", "icon": "mark_email_read", "tags": ["Queue", "Provider"], "route": "/services"},
                ],
            },
            {
                "title": "Dependency Watch",
                "caption": "Services with elevated shared dependency risk",
                "items": [
                    {"title": "Payment gateway", "detail": "Checkout and callback workers share gateway error-budget risk.", "status": "Watch", "icon": "payments"},
                    {"title": "Session cache", "detail": "Identity and customer session APIs depend on Redis memory policy stability.", "status": "Watch", "icon": "cached"},
                    {"title": "Internal DNS", "detail": "Service discovery remains a dependency for every critical API path.", "status": "Healthy", "icon": "dns"},
                ],
            },
        ],
    },
    "escalations": {
        "title": "Escalations",
        "subtitle": "Coordinate incident escalation ownership, policy paths, responder handoffs, and executive visibility.",
        "pill": {"icon": "outbound", "label": "Escalation center"},
        "kpis": [
            {"label": "Escalated Now", "value": "4", "helper": "Customer impact active", "icon": "campaign", "state": "critical"},
            {"label": "Pending Handoff", "value": "3", "helper": "Needs next responder", "icon": "swap_horiz", "state": "warning"},
            {"label": "Policy Breaches", "value": "1", "helper": "Exceeded handoff target", "icon": "gpp_bad", "state": "critical"},
            {"label": "Ack Rate", "value": "96%", "helper": "Last 24 hours", "icon": "how_to_reg", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Active Escalations",
                "caption": "Incidents currently needing senior review",
                "items": [
                    {"title": "Checkout latency spike", "subtitle": "INC-2026-000101", "detail": "Incident commander requested database and payment gateway owners on bridge.", "meta": "Policy: P1 customer checkout", "status": "Critical", "icon": "priority_high", "tags": ["Commander", "Bridge"], "route": "/incidents/101"},
                    {"title": "Authentication error spike", "subtitle": "INC-2026-000111", "detail": "Identity service release requires release manager and security owner sign-off.", "meta": "Policy: Auth outage", "status": "Critical", "icon": "security", "tags": ["Identity", "Release"], "route": "/incidents/111"},
                    {"title": "Database replica lag", "subtitle": "INC-2026-000110", "detail": "Replica freshness risk routed to database platform and reporting owners.", "meta": "Policy: Data consistency", "status": "High", "icon": "storage", "tags": ["Database"], "route": "/incidents/110"},
                ],
            },
            {
                "title": "Escalation Policy",
                "caption": "Current response expectations",
                "items": [
                    {"title": "P1 acknowledgement", "detail": "Incident commander and primary owner must acknowledge within 5 minutes.", "status": "Enforced", "icon": "timer"},
                    {"title": "Customer impact update", "detail": "External status update must be drafted within 15 minutes for active customer impact.", "status": "Enforced", "icon": "record_voice_over"},
                    {"title": "Handoff validation", "detail": "Next responder must accept ownership before the current owner leaves bridge.", "status": "Enforced", "icon": "verified"},
                ],
            },
        ],
    },
    "model-monitoring": {
        "title": "Model Monitoring",
        "subtitle": "Track prediction quality, confidence distribution, model version, and root-cause drift.",
        "pill": {"icon": "model_training", "label": "dt-v1.1.0"},
        "kpis": [
            {"label": "Accuracy", "value": "95.16%", "helper": "Held-out test set", "icon": "analytics", "state": "healthy"},
            {"label": "Model Size", "value": "460 KB", "helper": "Decision tree artifact", "icon": "inventory_2", "state": "healthy"},
            {"label": "Avg Confidence", "value": "89%", "helper": "Saved predictions", "icon": "psychology", "state": "healthy"},
            {"label": "Drift Watch", "value": "2", "helper": "Root causes elevated", "icon": "trending_up", "state": "warning"},
        ],
        "sections": [
            {
                "title": "Model Health",
                "caption": "Decision Tree production readiness",
                "items": [
                    {"title": "DecisionTreeClassifier", "subtitle": "dt-v1.1.0", "detail": "Trained on priority, impact, urgency, SLA, reassignment, reopen, contact, category, symptom, and assignment signals.", "meta": "Nodes: 4,517 - Depth: 12 - Features: 13", "status": "Active", "icon": "account_tree", "progress": 95, "tags": ["Accuracy 95.16%", "5 classes"]},
                    {"title": "Confidence guardrail", "subtitle": "Prediction policy", "detail": "Predictions below 70% confidence require manual investigator validation before closure.", "meta": "Current average: 89%", "status": "Healthy", "icon": "rule", "progress": 89, "tags": ["Review"]},
                    {"title": "Root-cause drift", "subtitle": "Distribution watch", "detail": "Deployment Failure and Memory Leak are above the rolling baseline and need review.", "meta": "Window: last 30 incidents", "status": "Watch", "icon": "online_prediction", "progress": 64, "tags": ["Drift"]},
                ],
            },
            {
                "title": "Improvement Backlog",
                "caption": "Next model quality actions",
                "items": [
                    {"title": "Add cross-validation report", "detail": "Store fold metrics and variance in model metadata after training.", "status": "Planned", "icon": "fact_check"},
                    {"title": "Capture prediction feedback", "detail": "Use investigator-confirmed root cause as future training labels.", "status": "Planned", "icon": "feedback"},
                    {"title": "Add drift alerts", "detail": "Notify admins when confidence drops or cause distribution shifts.", "status": "Planned", "icon": "notifications_active"},
                ],
            },
        ],
    },
    "data-sources": {
        "title": "Data Sources",
        "subtitle": "Manage connected log feeds, metric sources, CSV imports, and synchronization health.",
        "pill": {"icon": "storage", "label": "Admin only"},
        "kpis": [
            {"label": "Sources", "value": "9", "helper": "Logs, metrics, imports", "icon": "hub", "state": "healthy"},
            {"label": "Connected", "value": "7", "helper": "Currently healthy", "icon": "link", "state": "healthy"},
            {"label": "Warnings", "value": "2", "helper": "Needs credential review", "icon": "warning", "state": "warning"},
            {"label": "Last Sync", "value": "4m", "helper": "Most recent source update", "icon": "sync", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Source Connections",
                "caption": "Inbound operational data",
                "items": [
                    {"title": "Incident event CSV import", "subtitle": "incident_event_log.csv", "detail": "Historical ServiceNow incident event records used for model training and sample evidence.", "meta": "Last import: Aug 26, 2026 2:17 PM", "status": "Connected", "icon": "upload_file", "tags": ["CSV", "Training"]},
                    {"title": "Application logs", "subtitle": "TXT / LOG / CSV uploads", "detail": "Uploaded incident logs are parsed and stored in the logs table for investigation evidence.", "meta": "Owner: Platform Admin", "status": "Connected", "icon": "article", "tags": ["Logs"]},
                    {"title": "Metrics feed", "subtitle": "CPU, memory, latency, errors", "detail": "Metric records are linked to incidents and used by dashboard and investigation views.", "meta": "Owner: Observability", "status": "Connected", "icon": "monitoring", "tags": ["Metrics"]},
                    {"title": "Notification stream", "subtitle": "User alert feed", "detail": "Unread alert counts and notification menu details are loaded from the notifications table.", "meta": "Owner: App Admin", "status": "Warning", "icon": "notifications", "tags": ["Alerts"]},
                ],
            },
            {
                "title": "Admin Sync Tasks",
                "caption": "Data quality checks",
                "items": [
                    {"title": "Validate CSV schema", "detail": "Confirm required incident, state, SLA, caller, category, and assignment columns are present.", "status": "Ready", "icon": "rule"},
                    {"title": "Refresh model artifacts", "detail": "Retrain Decision Tree after confirmed postmortem labels are added.", "status": "Planned", "icon": "model_training"},
                    {"title": "Credential rotation", "detail": "Review API and database connection credentials before production deployment.", "status": "Warning", "icon": "key"},
                ],
            },
        ],
    },
    "audit-trail": {
        "title": "Audit Trail",
        "subtitle": "Review system access, user changes, incident updates, imports, exports, and investigation actions.",
        "pill": {"icon": "policy", "label": "Admin review"},
        "kpis": [
            {"label": "Events Today", "value": "28", "helper": "Recorded audit actions", "icon": "history", "state": "healthy"},
            {"label": "Role Changes", "value": "4", "helper": "User access updates", "icon": "admin_panel_settings", "state": "warning"},
            {"label": "Exports", "value": "6", "helper": "Reports and user data", "icon": "download", "state": "healthy"},
            {"label": "Blocked", "value": "2", "helper": "Permission denials", "icon": "block", "state": "critical"},
        ],
        "sections": [
            {
                "title": "Recent System Events",
                "caption": "Security and compliance activity",
                "items": [
                    {"title": "admin@example.com", "subtitle": "users:create", "detail": "Created a new investigator account and assigned platform access.", "meta": "Resource: User Management - 10:42 AM", "status": "Allowed", "icon": "person_add", "tags": ["Users"]},
                    {"title": "investigator@example.com", "subtitle": "incident:update", "detail": "Updated evidence notes and mitigation status for checkout latency spike.", "meta": "Resource: INC-2026-000101 - 10:36 AM", "status": "Allowed", "icon": "edit_note", "tags": ["Incident"]},
                    {"title": "viewer@example.com", "subtitle": "reports:export", "detail": "Attempted to export reports without export permission.", "meta": "Resource: Reports - 10:21 AM", "status": "Blocked", "icon": "block", "tags": ["Reports"]},
                    {"title": "admin@example.com", "subtitle": "data:import", "detail": "Imported historical incident event CSV evidence.", "meta": "Resource: Logs - 9:58 AM", "status": "Allowed", "icon": "upload_file", "tags": ["Import"]},
                ],
            },
            {
                "title": "Review Queue",
                "caption": "Audit items requiring attention",
                "items": [
                    {"title": "Permission denial review", "detail": "Confirm repeated report export denials are expected for viewer role.", "status": "Open", "icon": "gpp_maybe"},
                    {"title": "Role assignment validation", "detail": "Review admin user changes against access request records.", "status": "Open", "icon": "assignment_ind"},
                    {"title": "Export attestation", "detail": "Confirm report exports were business-approved and logged.", "status": "Pending", "icon": "fact_check"},
                ],
            },
        ],
    },
    "settings": {
        "title": "System Settings",
        "subtitle": "Review incident defaults, SLA thresholds, alert behavior, and platform administration settings.",
        "pill": {"icon": "settings", "label": "Admin only"},
        "kpis": [
            {"label": "SLA Target", "value": "99.5%", "helper": "Monthly service objective", "icon": "track_changes", "state": "healthy"},
            {"label": "Critical Ack", "value": "5m", "helper": "P1 acknowledgement", "icon": "timer", "state": "healthy"},
            {"label": "Alert Routes", "value": "6", "helper": "Notification policies", "icon": "alt_route", "state": "healthy"},
            {"label": "MFA Policy", "value": "On", "helper": "Required for admins", "icon": "security", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Incident Defaults",
                "caption": "Operational policy values",
                "items": [
                    {"title": "Default assignment", "subtitle": "Investigator queue", "detail": "New incidents are assigned to the active investigator group unless an owner is selected.", "meta": "Applied on create", "status": "Enabled", "icon": "assignment_ind"},
                    {"title": "Critical SLA threshold", "subtitle": "P1 response", "detail": "Critical incidents require acknowledgement in 5 minutes and commander review in 15 minutes.", "meta": "Policy: active", "status": "Enabled", "icon": "timer"},
                    {"title": "Evidence requirement", "subtitle": "Closure control", "detail": "Resolved incidents should include logs, metric snapshots, and a prevention step before closure.", "meta": "Policy: recommended", "status": "Enabled", "icon": "fact_check"},
                ],
            },
            {
                "title": "Platform Controls",
                "caption": "Administrative configuration",
                "items": [
                    {"title": "Admin MFA", "detail": "Administrative accounts require multi-factor authentication.", "status": "Enabled", "icon": "verified_user"},
                    {"title": "Audit exports", "detail": "Report and user exports are written to the audit trail.", "status": "Enabled", "icon": "history"},
                    {"title": "Model retraining", "detail": "Manual retraining is available to admins after new labeled evidence is imported.", "status": "Manual", "icon": "model_training"},
                ],
            },
        ],
    },
}
