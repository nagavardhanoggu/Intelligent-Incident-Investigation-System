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
        "subtitle": "Review logs, metrics, predictions, timeline events, uploaded artifacts, and validation gaps in one investigation view.",
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
                    {"title": "Reporting worker memory growth", "subtitle": "INC-2026-000115", "detail": "Heap-growth telemetry, export worker logs, GC pause samples, and mitigation notes are attached for review.", "meta": "Last indexed: Jul 29, 2026 9:28 PM", "status": "Complete", "icon": "memory", "tags": ["Heap", "Reports"], "route": "/incidents/115"},
                    {"title": "DNS resolver packet loss", "subtitle": "INC-2026-000106", "detail": "Resolver traces, failed lookup samples, network policy change notes, and recovery checks are grouped together.", "meta": "Last indexed: Apr 24, 2026 7:06 AM", "status": "Review", "icon": "dns", "tags": ["Network", "DNS"], "route": "/incidents/106"},
                    {"title": "Order event consumer lag", "subtitle": "INC-2026-000109", "detail": "Consumer lag charts, poison-event logs, replay output, and dead-letter queue changes support the final cause.", "meta": "Last indexed: May 28, 2026 5:44 PM", "status": "Pending", "icon": "queue", "tags": ["Kafka", "Replay"], "route": "/incidents/109"},
                ],
            },
            {
                "title": "Evidence Gaps",
                "caption": "Follow-up items before closure",
                "items": [
                    {"title": "Attach post-mitigation CPU window", "detail": "Checkout service needs 30 minutes of stable CPU and latency data.", "status": "Open", "icon": "show_chart", "tags": ["Metrics"]},
                    {"title": "Upload resolver traces", "detail": "DNS incident should include failed lookup samples from both affected zones.", "status": "Open", "icon": "dns", "tags": ["Network"]},
                    {"title": "Confirm dead-letter replay output", "detail": "Order event consumer requires replay count and failed-event quarantine evidence.", "status": "Pending", "icon": "fact_check", "tags": ["Kafka"]},
                    {"title": "Link readiness probe diff", "detail": "Checkout readiness failure needs the deployment diff that removed the previous health endpoint.", "status": "Open", "icon": "rocket_launch", "tags": ["Deployment"]},
                    {"title": "Verify provider throttling samples", "detail": "Notification queue evidence should include provider response codes from the impact window.", "status": "Review", "icon": "mark_email_read", "tags": ["Provider"]},
                    {"title": "Attach customer-impact note", "detail": "Critical incidents should retain a concise business impact summary before final closure.", "status": "Required", "icon": "assignment", "tags": ["Impact"]},
                ],
            },
            {
                "title": "Correlation Workbench",
                "caption": "Signals matched across source systems",
                "items": [
                    {"title": "Timeline alignment", "detail": "Deployment, alert, metric spike, log error, mitigation, and recovery events are compared in incident order.", "status": "Ready", "icon": "timeline", "tags": ["Timeline"], "route": "/investigation"},
                    {"title": "Metric anomaly windows", "detail": "Peak CPU, memory, latency, error rate, and database connections stay tied to exact capture timestamps.", "status": "Indexed", "icon": "query_stats", "tags": ["Metrics"], "route": "/metrics"},
                    {"title": "Prediction evidence review", "detail": "Root-cause predictions retain confidence, model version, and feature payload before the final cause is accepted.", "status": "Active", "icon": "online_prediction", "tags": ["ML"], "route": "/root-cause"},
                    {"title": "Resolution match", "detail": "Resolved incidents and prevention steps can be linked to reusable knowledge articles and runbooks.", "status": "Available", "icon": "library_books", "tags": ["Knowledge"], "route": "/knowledge-base"},
                ],
            },
            {
                "title": "Evidence Quality Controls",
                "caption": "Checks used by investigators before sign-off",
                "items": [
                    {"title": "Source ownership", "detail": "Each package should show who uploaded or generated the artifact and which system produced it.", "status": "Required", "icon": "person_search", "tags": ["Ownership"]},
                    {"title": "Completeness review", "detail": "Closure-ready incidents need logs, metrics, timeline context, mitigation notes, and recovery validation.", "status": "Required", "icon": "checklist", "tags": ["Closure"]},
                    {"title": "Sensitive data screening", "detail": "Secrets, tokens, and customer-sensitive values must be removed before evidence is retained.", "status": "Enforced", "icon": "shield", "tags": ["Security"]},
                    {"title": "Post-fix validation", "detail": "Investigators should attach stable telemetry after mitigation to prove the service returned to baseline.", "status": "Review", "icon": "task_alt", "tags": ["Validation"]},
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
                    {"title": "admin@example.com", "detailKey": "admin-users-create", "subtitle": "users:create", "detail": "Created a new investigator account and assigned platform access.", "meta": "Resource: User Management - 10:42 AM", "status": "Allowed", "icon": "person_add", "tags": ["Users"]},
                    {"title": "investigator@example.com", "subtitle": "incident:update", "detail": "Updated evidence notes and mitigation status for checkout latency spike.", "meta": "Resource: INC-2026-000101 - 10:36 AM", "status": "Allowed", "icon": "edit_note", "tags": ["Incident"]},
                    {"title": "viewer@example.com", "subtitle": "reports:export", "detail": "Attempted to export reports without export permission.", "meta": "Resource: Reports - 10:21 AM", "status": "Blocked", "icon": "block", "tags": ["Reports"]},
                    {"title": "admin@example.com", "detailKey": "admin-data-import", "subtitle": "data:import", "detail": "Imported historical incident event CSV evidence.", "meta": "Resource: Logs - 9:58 AM", "status": "Allowed", "icon": "upload_file", "tags": ["Import"]},
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


DEFAULT_OPERATION_PAGES = {
    "ml-training-options": {
        "defaults": {
            "priority": "MEDIUM",
            "impact": "MEDIUM",
            "urgency": "MEDIUM",
            "reassignment_count": 5,
            "reopen_count": 3,
            "sla_status": "WITHIN_SLA",
            "category": "CATEGORY 26",
            "subcategory": "SUBCATEGORY 174",
            "u_symptom": "SYMPTOM 72",
            "assignment_group": "GROUP 56",
            "contact_type": "PHONE",
            "knowledge": "TRUE",
            "sys_mod_count": 4,
        },
        "options": {
            "priority": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "impact": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "urgency": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "sla_status": ["WITHIN_SLA", "AT_RISK", "BREACHED"],
            "category": [
                "CATEGORY 23",
                "CATEGORY 26",
                "CATEGORY 32",
                "CATEGORY 37",
                "CATEGORY 40",
                "CATEGORY 42",
                "CATEGORY 46",
                "CATEGORY 53",
                "CATEGORY 57",
                "CATEGORY 61",
            ],
            "subcategory": [
                "SUBCATEGORY 9",
                "SUBCATEGORY 43",
                "SUBCATEGORY 75",
                "SUBCATEGORY 135",
                "SUBCATEGORY 164",
                "SUBCATEGORY 170",
                "SUBCATEGORY 174",
                "SUBCATEGORY 175",
                "SUBCATEGORY 223",
                "SUBCATEGORY 303",
            ],
            "u_symptom": [
                "SYMPTOM 4",
                "SYMPTOM 15",
                "SYMPTOM 72",
                "SYMPTOM 87",
                "SYMPTOM 88",
                "SYMPTOM 122",
                "SYMPTOM 211",
                "SYMPTOM 401",
                "SYMPTOM 471",
                "SYMPTOM 534",
            ],
            "assignment_group": [
                "GROUP 12",
                "GROUP 18",
                "GROUP 24",
                "GROUP 25",
                "GROUP 28",
                "GROUP 31",
                "GROUP 39",
                "GROUP 44",
                "GROUP 56",
                "GROUP 70",
            ],
            "contact_type": ["PHONE", "SELF SERVICE", "EMAIL", "DIRECT OPENING"],
            "knowledge": ["TRUE", "FALSE"],
        },
    },
    "incident-form-options": {
        "defaults": {
            "priority": "HIGH",
            "impact": "HIGH",
            "urgency": "HIGH",
        },
        "options": {
            "priority": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "impact": ["LOW", "MEDIUM", "HIGH"],
            "urgency": ["LOW", "MEDIUM", "HIGH"],
            "status": ["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"],
        },
    },
    "service-health": {
        "title": "Service Health",
        "subtitle": "Monitor production services, ownership, dependencies, current operational risk, and linked incident signals.",
        "pill": {"icon": "sync", "label": "Live service view"},
        "kpis": [
            {"icon": "verified", "label": "Healthy Services", "value": "9/12", "helper": "Production services inside normal thresholds", "state": "healthy"},
            {"icon": "warning", "label": "At Risk", "value": "2", "helper": "Checkout and database tier need attention", "state": "warning"},
            {"icon": "priority_high", "label": "Critical", "value": "1", "helper": "Payment callback queue over threshold", "state": "critical"},
            {"icon": "hub", "label": "Dependency Alerts", "value": "4", "helper": "Database, cache, DNS, and queue dependencies", "state": "warning"},
        ],
        "sections": [
            {
                "title": "Service Inventory",
                "caption": "Customer-facing services and current health state",
                "items": [
                    {"icon": "shopping_cart", "title": "Checkout Service", "subtitle": "Tier 1 customer path", "detail": "P95 latency elevated after payment gateway rollout.", "meta": "Owner: Payments Platform", "status": "Critical", "tags": ["Checkout", "Payments", "P95"], "route": "/incidents/101"},
                    {"icon": "storage", "title": "Primary Database", "subtitle": "Orders and inventory state", "detail": "Connection usage remains under watch after saturation recovery.", "meta": "Owner: Data Reliability", "status": "Warning", "tags": ["Pool", "Replica"], "route": "/incidents/102"},
                    {"icon": "notifications", "title": "Notification Service", "subtitle": "Transactional alerts", "detail": "Heap usage stable after the cache guardrail change.", "meta": "Owner: Messaging", "status": "Healthy", "tags": ["Heap", "Queue"], "route": "/incidents/103"},
                    {"icon": "manage_search", "title": "Search Indexer", "subtitle": "Catalog refresh pipeline", "detail": "Refresh backlog cleared after malformed batch quarantine.", "meta": "Owner: Catalog Platform", "status": "Healthy", "tags": ["Indexer", "Quarantine"], "route": "/incidents/108"},
                ],
            },
            {
                "title": "Key Dependencies",
                "caption": "Shared systems that can raise service risk",
                "items": [
                    {"icon": "payments", "title": "Payment Gateway", "detail": "Recent deployment correlated with checkout latency spike INC-2026-000101.", "status": "Warning", "tags": ["External", "Payments"], "route": "/incidents/101"},
                    {"icon": "cached", "title": "Session Cache", "detail": "Eviction guardrails restored after April cache incident.", "status": "Healthy", "tags": ["Redis", "Identity"], "route": "/incidents/105"},
                    {"icon": "dns", "title": "Internal DNS", "detail": "Synthetic lookup checks now cover both previously affected production zones.", "status": "Healthy", "tags": ["Service discovery"], "route": "/incidents/106"},
                    {"icon": "queue", "title": "Notification Queue", "detail": "Message age and retry backoff remain within target after provider throttling.", "status": "Healthy", "tags": ["Queue", "Email"], "route": "/incidents/112"},
                ],
            },
            {
                "title": "Related Incident Signals",
                "caption": "Evidence to review before declaring a service healthy",
                "items": [
                    {"icon": "monitoring", "title": "Latency signal", "detail": "Checkout response time peaked above customer-impact thresholds during the payment rollout.", "meta": "Source: Metrics overview", "status": "Critical", "tags": ["Latency"]},
                    {"icon": "article", "title": "Database pool logs", "detail": "Connection-pool exhaustion records remain attached to the database saturation investigation.", "meta": "Source: Log index", "status": "Complete", "tags": ["Logs"]},
                    {"icon": "timeline", "title": "Recovery timeline", "detail": "Mitigation and recovery events are available for correlated incident review.", "meta": "Source: Investigation timeline", "status": "Complete", "tags": ["Timeline"]},
                    {"icon": "task_alt", "title": "Prevention check", "detail": "Service owners should confirm guardrails before moving watch services to healthy.", "meta": "Source: Resolution knowledge", "status": "Pending", "tags": ["Prevention"]},
                ],
            },
        ],
    },
    "deployments": {
        "title": "Deployments",
        "subtitle": "Review production changes, correlate deployments with incidents, and verify rollback readiness.",
        "pill": {"icon": "rocket_launch", "label": "Release activity"},
        "kpis": [
            {"icon": "rocket_launch", "label": "Deployments", "value": "18", "helper": "Production changes in the last 14 days", "state": "healthy"},
            {"icon": "undo", "label": "Rollbacks", "value": "2", "helper": "Tied to readiness or routing regressions", "state": "warning"},
            {"icon": "tune", "label": "Canary Coverage", "value": "82%", "helper": "Critical services using staged rollout", "state": "healthy"},
            {"icon": "link", "label": "Change Incidents", "value": "5", "helper": "Recent incidents with deployment correlation", "state": "warning"},
        ],
        "sections": [
            {
                "title": "Recent Deployments",
                "caption": "Production changes with operational impact",
                "items": [
                    {"icon": "payments", "title": "Payment Gateway v4.8.2", "subtitle": "Checkout payment path", "detail": "Checkout latency increased within five minutes of release.", "meta": "Owner: Payments Platform", "status": "Critical", "tags": ["Rollback", "Checkout"], "route": "/incidents/101"},
                    {"icon": "key", "title": "Identity Service Key Rotation", "subtitle": "Authentication service", "detail": "Rollback completed after cached signing-key mismatch.", "meta": "Owner: Identity", "status": "Warning", "tags": ["Auth", "Keys"], "route": "/incidents/111"},
                    {"icon": "sync_alt", "title": "Inventory Sync Partitioning", "subtitle": "Warehouse update workers", "detail": "Feature flag restored parallel warehouse updates.", "meta": "Owner: Supply Chain", "status": "Healthy", "tags": ["Feature flag"], "route": "/incidents/114"},
                    {"icon": "search", "title": "Search Indexer Retry Guard", "subtitle": "Catalog indexing", "detail": "Malformed batch quarantine deployed successfully.", "meta": "Owner: Catalog Platform", "status": "Healthy", "tags": ["Retry", "Quarantine"], "route": "/incidents/108"},
                ],
            },
            {
                "title": "Rollback Checklist",
                "caption": "Controls required for incident-linked changes",
                "items": [
                    {"icon": "inventory_2", "title": "Rollback Package", "detail": "Validated images and configuration snapshots are attached for payment and identity services.", "status": "Ready", "tags": ["Images", "Config"]},
                    {"icon": "rule", "title": "Canary Exit Gate", "detail": "P95 latency, auth failures, and queue depth must stay under thresholds for 30 minutes.", "status": "Enforced", "tags": ["Canary"]},
                    {"icon": "timeline", "title": "Incident Linkage", "detail": "Changes are linked to investigation timelines for correlation and reporting.", "status": "Complete", "tags": ["Timeline"]},
                    {"icon": "fact_check", "title": "Post-release Evidence", "detail": "Owners must attach metric snapshots and rollback decision notes after customer-facing releases.", "status": "Pending", "tags": ["Evidence"]},
                ],
            },
            {
                "title": "Change Risk Review",
                "caption": "What investigators should inspect next",
                "items": [
                    {"icon": "query_stats", "title": "Metric comparison", "detail": "Compare pre-release and post-release latency for each customer-facing path.", "status": "Open", "tags": ["Metrics"]},
                    {"icon": "account_tree", "title": "Dependency diff", "detail": "Review configuration and route changes against service-catalog dependencies.", "status": "Open", "tags": ["Dependencies"]},
                    {"icon": "support_agent", "title": "Owner acknowledgement", "detail": "Confirm the service owner and incident commander accepted the rollback decision.", "status": "Pending", "tags": ["On-call"]},
                    {"icon": "history_edu", "title": "Learning capture", "detail": "Incident-linked deployments should create a postmortem prevention item.", "status": "Planned", "tags": ["Postmortem"]},
                ],
            },
        ],
    },
    "change-calendar": {
        "title": "Change Calendar",
        "subtitle": "Track production changes, release windows, freeze periods, and incident-linked deployment risk.",
        "pill": {"icon": "event", "label": "Release schedule"},
        "kpis": [
            {"icon": "event", "label": "Scheduled Changes", "value": "7", "helper": "Approved production windows this week", "state": "healthy"},
            {"icon": "report", "label": "High Risk", "value": "2", "helper": "Payment and database changes require incident watch", "state": "warning"},
            {"icon": "event_busy", "label": "Freeze Windows", "value": "1", "helper": "Checkout peak sale freeze starts Friday", "state": "warning"},
            {"icon": "fact_check", "label": "CAB Approval", "value": "94%", "helper": "Changes with required approvals complete", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Scheduled Changes",
                "caption": "Upcoming releases with operational ownership",
                "items": [
                    {"icon": "credit_card", "title": "Checkout Payment Gateway Patch", "subtitle": "Customer payment path", "detail": "Canary release with active incident observer assigned.", "meta": "Owner: Payments Platform", "status": "Warning", "tags": ["Canary", "Checkout"], "route": "/deployments"},
                    {"icon": "storage", "title": "Database Pool Limit Review", "subtitle": "Primary database", "detail": "Connection settings update after saturation incident.", "meta": "Owner: Data Reliability", "status": "Warning", "tags": ["Database", "Pool"], "route": "/incidents/102"},
                    {"icon": "dns", "title": "DNS Policy Validation", "subtitle": "Service discovery", "detail": "Non-disruptive synthetic checks across two zones.", "meta": "Owner: Network Reliability", "status": "Healthy", "tags": ["DNS"], "route": "/incidents/106"},
                    {"icon": "mark_email_read", "title": "Notification Backoff Release", "subtitle": "Email provider throttling", "detail": "Retry backoff deployment for transactional email throttling.", "meta": "Owner: Messaging", "status": "Healthy", "tags": ["Queue", "Email"], "route": "/incidents/112"},
                ],
            },
            {
                "title": "Change Controls",
                "caption": "Governance rules for release safety",
                "items": [
                    {"icon": "visibility", "title": "Incident Watch", "detail": "High-risk changes require on-call acknowledgement and dashboard monitoring.", "status": "Enforced", "tags": ["Monitoring"]},
                    {"icon": "event_busy", "title": "Freeze Policy", "detail": "Checkout and payment releases are blocked during peak order windows unless approved as urgent fixes.", "status": "Enabled", "tags": ["Freeze"]},
                    {"icon": "rate_review", "title": "Post-change Review", "detail": "Every incident-linked deployment needs a rollback and prevention note within 24 hours.", "status": "Required", "tags": ["Review"]},
                    {"icon": "approval", "title": "CAB Evidence", "detail": "Critical service changes must include approval, rollback owner, and impact notes before release.", "status": "Required", "tags": ["Approval"]},
                ],
            },
            {
                "title": "Incident Windows",
                "caption": "Release windows with linked investigation context",
                "items": [
                    {"icon": "timer", "title": "Checkout observation window", "detail": "Monitor latency, gateway errors, and payment callback queues during release.", "status": "Active", "tags": ["P1", "Checkout"]},
                    {"icon": "storage", "title": "Database safeguard window", "detail": "Track connection wait time and slow query counts after pool configuration changes.", "status": "Planned", "tags": ["Database"]},
                    {"icon": "campaign", "title": "Customer impact readiness", "detail": "Status update owners are assigned before customer-facing changes start.", "status": "Ready", "tags": ["Comms"]},
                    {"icon": "task_alt", "title": "Closeout evidence", "detail": "Release owners must attach post-change metric evidence before closing the change.", "status": "Pending", "tags": ["Evidence"]},
                ],
            },
        ],
    },
    "sla-monitor": {
        "title": "SLA Monitor",
        "subtitle": "Track SLA health, breach risk, response windows, and operational commitments across active incidents.",
        "pill": {"icon": "timer", "label": "73.3% SLA"},
        "kpis": [
            {"icon": "timer", "label": "SLA Compliance", "value": "73.3%", "helper": "Computed from tracked incidents", "state": "warning"},
            {"icon": "gpp_bad", "label": "Breaches", "value": "4", "helper": "Incidents outside committed window", "state": "critical"},
            {"icon": "running_with_errors", "label": "At Risk", "value": "3", "helper": "Active services near breach threshold", "state": "warning"},
            {"icon": "schedule", "label": "Avg MTTR", "value": "67m", "helper": "Resolved incident average", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "SLA Risk Queue",
                "caption": "Services and incidents nearest to breach",
                "items": [
                    {"icon": "shopping_cart", "title": "Checkout Service", "subtitle": "Critical customer path", "detail": "Critical incident approaching customer-impact SLA.", "meta": "Owner: Payments Platform", "status": "Critical", "tags": ["P1", "Checkout"], "route": "/incidents/101"},
                    {"icon": "storage", "title": "Database Connections", "subtitle": "Connection pool wait time", "detail": "Connection wait time recovered but remains under watch.", "meta": "Owner: Data Reliability", "status": "Warning", "tags": ["Pool"], "route": "/incidents/102"},
                    {"icon": "mail", "title": "Notification Queue", "subtitle": "Message age", "detail": "Message age within target after retry backoff tuning.", "meta": "Owner: Messaging", "status": "Healthy", "tags": ["Queue"], "route": "/incidents/112"},
                    {"icon": "verified_user", "title": "Authentication Service", "subtitle": "Login error rate", "detail": "Auth failures recovered after signing-key cache refresh.", "meta": "Owner: Identity", "status": "Healthy", "tags": ["Auth"], "route": "/incidents/111"},
                ],
            },
            {
                "title": "SLA Policies",
                "caption": "Response and review rules",
                "items": [
                    {"icon": "priority_high", "title": "Critical Response", "detail": "Acknowledge within 5 minutes and provide status update every 15 minutes.", "status": "Enforced", "tags": ["P1"]},
                    {"icon": "support_agent", "title": "High Priority Recovery", "detail": "Restore customer-facing paths within 60 minutes or escalate to incident command.", "status": "Enforced", "tags": ["P2"]},
                    {"icon": "history_edu", "title": "Breach Review", "detail": "Every breach requires a prevention action and knowledge-base article.", "status": "Required", "tags": ["Review"]},
                    {"icon": "notifications_active", "title": "Approaching Breach Alert", "detail": "Alert rules notify the primary responder before an active incident crosses the SLA target.", "status": "Enabled", "tags": ["Alerts"]},
                ],
            },
            {
                "title": "Recovery Evidence",
                "caption": "Signals needed before SLA closure",
                "items": [
                    {"icon": "monitoring", "title": "Stable metric window", "detail": "Attach at least 30 minutes of stable latency and error-rate data.", "status": "Required", "tags": ["Metrics"]},
                    {"icon": "article", "title": "Log confirmation", "detail": "Link logs showing the failure stopped after mitigation.", "status": "Required", "tags": ["Logs"]},
                    {"icon": "task_alt", "title": "Owner validation", "detail": "Service owner confirms customer-facing workflows have recovered.", "status": "Pending", "tags": ["Owner"]},
                    {"icon": "library_books", "title": "Knowledge update", "detail": "Resolution article is updated when the incident creates reusable recovery steps.", "status": "Planned", "tags": ["Knowledge"]},
                ],
            },
        ],
    },
    "alert-rules": {
        "title": "Alert Rules",
        "subtitle": "Review operational alert policies, thresholds, routing logic, and ML-assisted triage rules.",
        "pill": {"icon": "notifications_active", "label": "Rule coverage"},
        "kpis": [
            {"icon": "notifications_active", "label": "Active Rules", "value": "42", "helper": "Rules evaluating production telemetry", "state": "healthy"},
            {"icon": "psychology", "label": "ML Assisted", "value": "11", "helper": "Rules linked to prediction signals", "state": "healthy"},
            {"icon": "volume_off", "label": "Noise Reduction", "value": "28%", "helper": "Suppressed duplicate alerts this week", "state": "healthy"},
            {"icon": "call_split", "label": "Escalations", "value": "6", "helper": "Rules with paging escalation", "state": "warning"},
        ],
        "sections": [
            {
                "title": "Alert Rule Catalog",
                "caption": "Rules tied to incident intake and evidence correlation",
                "items": [
                    {"icon": "speed", "title": "Checkout P95 Latency", "subtitle": "Customer checkout path", "detail": "Critical when P95 exceeds 2s for five minutes.", "meta": "Owner: Payments Platform", "status": "Critical", "tags": ["Latency", "P1"], "route": "/incidents/101"},
                    {"icon": "storage", "title": "Database Pool Saturation", "subtitle": "Connection pool", "detail": "Warn at 80 percent, critical at exhausted pool.", "meta": "Owner: Data Reliability", "status": "Warning", "tags": ["Database"], "route": "/incidents/102"},
                    {"icon": "dns", "title": "DNS Resolver Errors", "subtitle": "Service discovery", "detail": "Detect zone-level service discovery failures.", "meta": "Owner: Network Reliability", "status": "Healthy", "tags": ["DNS"], "route": "/incidents/106"},
                    {"icon": "memory", "title": "Heap Growth Rate", "subtitle": "Runtime memory", "detail": "Alert on continuous growth after full GC cycles.", "meta": "Owner: Runtime Platform", "status": "Healthy", "tags": ["Heap"], "route": "/incidents/115"},
                ],
            },
            {
                "title": "Routing Logic",
                "caption": "Escalation and grouping behavior",
                "items": [
                    {"icon": "campaign", "title": "Critical Path Paging", "detail": "Checkout, payment, authentication, and database alerts page primary and incident command.", "status": "Enforced", "tags": ["Paging"]},
                    {"icon": "online_prediction", "title": "ML Prediction Signal", "detail": "Root cause confidence over 85 percent adds the related specialist team to the alert context.", "status": "Active", "tags": ["ML"]},
                    {"icon": "join_inner", "title": "Duplicate Suppression", "detail": "Alerts sharing incident key and metric source are grouped for 20 minutes.", "status": "Enabled", "tags": ["Noise"]},
                    {"icon": "outbound", "title": "Escalation Handoff", "detail": "Unacknowledged critical alerts are routed to the secondary owner and incident commander.", "status": "Enabled", "tags": ["Escalation"]},
                ],
            },
            {
                "title": "Tuning Backlog",
                "caption": "Rules that need threshold or routing review",
                "items": [
                    {"icon": "query_stats", "title": "Latency baseline refresh", "detail": "Update checkout thresholds after payment gateway mitigation stabilizes.", "status": "Planned", "tags": ["Checkout"]},
                    {"icon": "storage", "title": "Pool saturation forecast", "detail": "Add forecast warning before the pool reaches hard exhaustion.", "status": "Open", "tags": ["Database"]},
                    {"icon": "notifications_paused", "title": "Notification retry noise", "detail": "Group provider throttling retries by campaign and route.", "status": "Open", "tags": ["Messaging"]},
                    {"icon": "fact_check", "title": "Rule coverage audit", "detail": "Compare alert rules against critical service catalog dependencies.", "status": "Pending", "tags": ["Audit"]},
                ],
            },
        ],
    },
    "on-call": {
        "title": "On-Call",
        "subtitle": "Review active responders, escalation ownership, acknowledgement health, and support coverage.",
        "pill": {"icon": "support_agent", "label": "Current shift"},
        "kpis": [
            {"icon": "support_agent", "label": "Primary Responders", "value": "4", "helper": "Currently assigned across incident domains", "state": "healthy"},
            {"icon": "task_alt", "label": "Ack Median", "value": "3m", "helper": "Median acknowledgement time today", "state": "healthy"},
            {"icon": "call_made", "label": "Escalations", "value": "2", "helper": "Open escalations needing secondary owner", "state": "warning"},
            {"icon": "verified_user", "label": "Coverage", "value": "100%", "helper": "All critical services have active coverage", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Responder Queue",
                "caption": "Current people and coverage areas",
                "items": [
                    {"icon": "person_search", "title": "Investigator User", "subtitle": "Incident Response", "detail": "Primary responder for checkout and database incidents.", "meta": "Team: Incident Response", "status": "Warning", "tags": ["Checkout", "Database"], "route": "/account/access-role"},
                    {"icon": "engineering", "title": "Neha Sharma", "subtitle": "Application Reliability", "detail": "Secondary responder for application workflow failures.", "meta": "Team: Application Reliability", "status": "Healthy", "tags": ["Application"]},
                    {"icon": "admin_panel_settings", "title": "Admin User", "subtitle": "Platform Operations", "detail": "Incident commander for critical escalation windows.", "meta": "Team: Platform Operations", "status": "Healthy", "tags": ["Commander"], "route": "/account/profile"},
                    {"icon": "manage_accounts", "title": "Sana Khan", "subtitle": "Operations Admin", "detail": "Access administration backup for user-impacting incidents.", "meta": "Team: Operations Admin", "status": "Warning", "tags": ["Access"]},
                ],
            },
            {
                "title": "Escalation Rules",
                "caption": "Routing rules used during active incidents",
                "items": [
                    {"icon": "priority_high", "title": "Critical Escalation", "detail": "Page incident command after two missed acknowledgements or 15 minutes without mitigation.", "status": "Enforced", "tags": ["P1"]},
                    {"icon": "account_tree", "title": "Specialist Routing", "detail": "Database, network, payment, and identity specialists are added based on root-cause prediction.", "status": "Active", "tags": ["ML"]},
                    {"icon": "notes", "title": "Handoff Notes", "detail": "Responders must attach current status, open risks, and next action before shift transfer.", "status": "Required", "tags": ["Handoff"]},
                    {"icon": "record_voice_over", "title": "Stakeholder Update", "detail": "Customer-impacting incidents require status-owner acknowledgement before the first update window.", "status": "Required", "tags": ["Comms"]},
                ],
            },
            {
                "title": "Coverage Review",
                "caption": "Gaps and follow-up items for the next shift",
                "items": [
                    {"icon": "timer", "title": "Database watch handoff", "detail": "Next responder should review pool recovery metrics before leaving database incident on watch.", "status": "Pending", "tags": ["Database"]},
                    {"icon": "shopping_cart", "title": "Checkout bridge coverage", "detail": "Keep payments specialist on bridge until checkout latency is stable.", "status": "Active", "tags": ["Checkout"]},
                    {"icon": "verified_user", "title": "Identity backup", "detail": "Confirm a secondary identity owner for any signing-key follow-up.", "status": "Ready", "tags": ["Auth"]},
                    {"icon": "library_books", "title": "Runbook ownership", "detail": "Assign owner updates for reused runbooks after active incident closure.", "status": "Planned", "tags": ["Runbooks"]},
                ],
            },
        ],
    },
    "root-cause": {
        "title": "Root Cause",
        "subtitle": "Review predicted root cause patterns, repeated failure modes, and prevention opportunities.",
        "pill": {"icon": "device_hub", "label": "Cause intelligence"},
        "kpis": [
            {"icon": "psychology", "label": "Predictions", "value": "15", "helper": "Stored model results across incidents", "state": "healthy"},
            {"icon": "account_tree", "label": "Top Cause", "value": "Application", "helper": "Most common confirmed category", "state": "warning"},
            {"icon": "insights", "label": "Avg Confidence", "value": "88%", "helper": "Decision tree confidence across stored results", "state": "healthy"},
            {"icon": "checklist", "label": "Prevention Items", "value": "15", "helper": "Resolution articles with follow-up steps", "state": "healthy"},
        ],
        "sections": [
            {
                "title": "Root Cause Patterns",
                "caption": "Failure modes observed across incidents",
                "items": [
                    {"icon": "bug_report", "title": "Application Failure", "subtitle": "Workflow and payload failures", "detail": "Workflow defects, malformed payloads, and unsafe feature flag behavior.", "meta": "Owner: Application Reliability", "status": "Warning", "tags": ["Recurring"], "route": "/knowledge-base"},
                    {"icon": "rocket_launch", "title": "Deployment Failure", "subtitle": "Release validation gaps", "detail": "Routing, readiness, and release validation regressions.", "meta": "Owner: Release Engineering", "status": "Warning", "tags": ["Deployments"], "route": "/deployments"},
                    {"icon": "storage", "title": "Database Issue", "subtitle": "Connection and replica risk", "detail": "Connection saturation, replica lag, and workload isolation gaps.", "meta": "Owner: Data Reliability", "status": "Critical", "tags": ["Database"], "route": "/incidents/102"},
                    {"icon": "memory", "title": "Memory Leak", "subtitle": "Unbounded retention paths", "detail": "Unbounded retention paths in notification and reporting workloads.", "meta": "Owner: Runtime Platform", "status": "Warning", "tags": ["Heap"], "route": "/incidents/115"},
                    {"icon": "device_hub", "title": "Network Issue", "subtitle": "DNS and policy failures", "detail": "DNS and policy failures affecting service discovery.", "meta": "Owner: Network Reliability", "status": "Healthy", "tags": ["Network"], "route": "/incidents/106"},
                ],
            },
            {
                "title": "Prevention Focus",
                "caption": "Recommended controls to reduce repeat incidents",
                "items": [
                    {"icon": "storage", "title": "Close Repeat Database Risks", "detail": "Add query guards and pool saturation rollback for checkout and reporting paths.", "status": "Open", "tags": ["Database"]},
                    {"icon": "rocket_launch", "title": "Tighten Release Gates", "detail": "Require readiness probe and route-diff validation before critical service rollout.", "status": "Planned", "tags": ["Deployments"]},
                    {"icon": "queue", "title": "Expand Quarantine Paths", "detail": "Malformed events and catalog batches should move to dead-letter queues without blocking partitions.", "status": "In progress", "tags": ["Queues"]},
                    {"icon": "monitoring", "title": "Add Drift Alerts", "detail": "Notify admins when prediction confidence drops or root-cause distribution shifts.", "status": "Planned", "tags": ["Model"]},
                ],
            },
            {
                "title": "Investigation Evidence",
                "caption": "Database-backed signals behind cause analysis",
                "items": [
                    {"icon": "online_prediction", "title": "Stored predictions", "detail": "Prediction records retain cause, confidence, features, version, and timestamp for each analyzed incident.", "status": "Complete", "tags": ["Predictions"]},
                    {"icon": "library_books", "title": "Resolution knowledge", "detail": "Resolution articles provide prevention steps and confirmed root causes for repeat analysis.", "status": "Complete", "tags": ["Knowledge"]},
                    {"icon": "timeline", "title": "Timeline correlation", "detail": "Timeline events explain cause progression from alert through mitigation and recovery.", "status": "Complete", "tags": ["Timeline"]},
                    {"icon": "query_stats", "title": "Metric evidence", "detail": "Peak CPU, memory, latency, errors, and database connections support cause validation.", "status": "Complete", "tags": ["Metrics"]},
                ],
            },
        ],
    },
}


DEFAULT_OPERATIONAL_PAGES = {**DEFAULT_FEATURE_PAGES, **DEFAULT_OPERATION_PAGES}
