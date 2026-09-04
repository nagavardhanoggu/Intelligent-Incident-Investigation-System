from datetime import datetime, timedelta

from sqlalchemy import delete, inspect, select, text
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.feature_pages import DEFAULT_OPERATIONAL_PAGES
from app.models.entities import Incident, Log, Metric, OperationalPage, Permission, Prediction, Role, RolePermission, Timeline, User, UserAccountSettings, UserRole
from app.rbac import PERMISSIONS, ROLES, ROLE_PERMISSIONS
from app.utils.security import hash_password


DEFAULT_USERS = [
    ("Admin User", "admin@example.com", "ADMIN"),
    ("Investigator User", "investigator@example.com", "INVESTIGATOR"),
    ("Viewer User", "viewer@example.com", "VIEWER"),
]

DEFAULT_USER_PASSWORD = "password"

OBSOLETE_PERMISSIONS = {"operations:view"}

DEFAULT_INCIDENTS = [
    {
        "id": 101,
        "incident_key": "INC-2026-000101",
        "title": "Checkout latency spike",
        "description": "P95 checkout latency crossed threshold after payment gateway deployment.",
        "priority": "CRITICAL",
        "impact": "HIGH",
        "urgency": "HIGH",
        "status": "INVESTIGATING",
        "assigned_email": "investigator@example.com",
    },
    {
        "id": 102,
        "incident_key": "INC-2026-000102",
        "title": "Database connection saturation",
        "description": "API workers exhausted the database connection pool.",
        "priority": "HIGH",
        "impact": "HIGH",
        "urgency": "MEDIUM",
        "status": "OPEN",
        "assigned_email": "investigator@example.com",
    },
    {
        "id": 103,
        "incident_key": "INC-2026-000103",
        "title": "Memory growth in notification service",
        "description": "Heap usage increased steadily after a campaign event.",
        "priority": "MEDIUM",
        "impact": "MEDIUM",
        "urgency": "MEDIUM",
        "status": "RESOLVED",
        "assigned_email": "investigator@example.com",
    },
]

DEFAULT_TIMELINE_EVENTS = [
    (101, "2026-08-25T10:00:00", "Deployment", "Payment gateway deployment started", "CI/CD"),
    (101, "2026-08-25T10:02:00", "Restart", "Checkout service restarted", "Kubernetes"),
    (101, "2026-08-25T10:05:00", "Metric", "CPU usage spiked above 90%", "Metrics"),
    (101, "2026-08-25T10:06:00", "Error", "Database timeout errors increased", "Logs"),
    (101, "2026-08-25T10:08:00", "Failure", "Checkout failures breached SLA", "APM"),
    (102, "2026-08-26T08:40:00", "Alert", "Database connection utilization crossed the 80% warning threshold", "Prometheus"),
    (102, "2026-08-26T08:43:00", "Traffic", "API request concurrency increased after the morning traffic ramp", "API Gateway"),
    (102, "2026-08-26T08:46:00", "Saturation", "Application connection pool reached its configured limit of 200", "Database Monitor"),
    (102, "2026-08-26T08:48:00", "Degradation", "API workers began queueing while waiting for database connections", "APM"),
    (102, "2026-08-26T08:51:00", "Error", "Inventory and checkout endpoints started returning intermittent 503 responses", "Logs"),
    (102, "2026-08-26T08:56:00", "Mitigation", "On-call increased pool capacity and recycled stale idle connections", "Operations"),
    (102, "2026-08-26T09:02:00", "Recovery", "Connection wait time and API latency returned toward baseline", "APM"),
]

DEFAULT_METRICS = [
    (101, "2026-08-25T10:00:00", 62.0, 58.0, 71.0, 420.0, 0.8, 86),
    (101, "2026-08-25T10:03:00", 78.0, 64.0, 73.0, 980.0, 2.4, 132),
    (101, "2026-08-25T10:06:00", 91.4, 82.7, 77.5, 2300.5, 7.25, 214),
    (101, "2026-08-25T10:09:00", 87.0, 85.0, 78.2, 1900.0, 5.6, 198),
    (101, "2026-08-25T10:12:00", 69.0, 71.0, 75.0, 740.0, 1.4, 121),
    (102, "2026-08-26T08:40:00", 48.0, 61.0, 54.0, 310.0, 0.35, 124),
    (102, "2026-08-26T08:43:00", 56.0, 65.0, 55.0, 580.0, 0.90, 161),
    (102, "2026-08-26T08:46:00", 68.0, 72.0, 55.5, 1420.0, 3.80, 200),
    (102, "2026-08-26T08:49:00", 74.0, 78.0, 56.0, 2680.0, 8.40, 200),
    (102, "2026-08-26T08:52:00", 71.0, 80.0, 56.2, 2310.0, 6.75, 198),
    (102, "2026-08-26T08:56:00", 63.0, 74.0, 56.4, 1180.0, 2.10, 184),
    (102, "2026-08-26T09:02:00", 51.0, 66.0, 56.5, 430.0, 0.55, 139),
]

DEFAULT_LOGS = [
    {
        "incident_id": 102,
        "file_name": "db-pool-monitor.log",
        "file_type": "LOG",
        "storage_path": "uploads/seed/db-pool-monitor.log",
        "uploaded_at": "2026-08-26T08:58:00",
        "parsed_content": (
            "08:43:11 WARN  connection-pool active=161 idle=7 waiting=18 max=200\n"
            "08:46:03 ERROR connection-pool exhausted active=200 idle=0 waiting=64 max=200\n"
            "08:49:27 ERROR checkout timed out after 3000ms waiting for database connection\n"
            "08:56:42 INFO  connection-pool resized previous_max=200 new_max=260\n"
            "09:02:10 INFO  connection-pool active=139 idle=71 waiting=0 max=260"
        ),
    },
    {
        "incident_id": 102,
        "file_name": "api-worker-errors.log",
        "file_type": "LOG",
        "storage_path": "uploads/seed/api-worker-errors.log",
        "uploaded_at": "2026-08-26T08:59:00",
        "parsed_content": (
            "08:48:15 WARN  request queued service=inventory-api wait_ms=1180\n"
            "08:51:02 ERROR request failed service=checkout-api status=503 cause=db_connection_timeout\n"
            "08:52:44 ERROR request failed service=inventory-api status=503 cause=db_connection_timeout\n"
            "08:57:18 INFO  worker health recovered service=checkout-api available_connections=32"
        ),
    },
]

DEFAULT_PREDICTIONS = [
    {
        "incident_id": 101,
        "predicted_cause": "Database Issue",
        "confidence_score": 0.86,
        "model_version": "dt-v1.0.0",
        "model_features": {
            "priority": "CRITICAL",
            "impact": "HIGH",
            "urgency": "HIGH",
            "reassignment_count": 2,
            "reopen_count": 0,
            "sla_status": "AT_RISK",
        },
    },
    {
        "incident_id": 102,
        "predicted_cause": "Database Issue",
        "confidence_score": 0.92,
        "model_version": "dt-v1.0.0",
        "model_features": {
            "priority": "HIGH",
            "impact": "HIGH",
            "urgency": "MEDIUM",
            "reassignment_count": 1,
            "reopen_count": 0,
            "sla_status": "AT_RISK",
            "peak_database_connections": 200,
            "peak_response_time_ms": 2680,
        },
    },
]

DEFAULT_INVESTIGATION_PROFILES = {
    103: {
        "started_at": "2026-08-24T13:20:00",
        "component": "notification-service",
        "source": "Heap Monitor",
        "alert": "Notification service heap usage grew continuously after the campaign fan-out began",
        "symptom": "Garbage collection pauses increased while the template cache retained completed campaign objects",
        "impact": "Notification delivery latency exceeded five minutes for a subset of campaign messages",
        "diagnosis": "Heap analysis identified retained template objects as the dominant allocation path",
        "mitigation": "The service was restarted and the unbounded template cache was disabled",
        "cause": "Memory Leak",
        "confidence": 0.89,
        "peaks": (72.0, 95.0, 1480.0, 3.6, 110),
    },
    104: {
        "started_at": "2026-04-04T09:10:00",
        "component": "api-gateway",
        "source": "Gateway APM",
        "alert": "API gateway P95 latency increased immediately after a routing policy deployment",
        "symptom": "Request tracing showed an additional authentication middleware pass on every route",
        "impact": "Customer API requests exceeded the latency SLO and produced intermittent timeouts",
        "diagnosis": "The deployed routing policy duplicated authentication middleware execution",
        "mitigation": "Operations rolled back the routing policy and recycled the gateway pods",
        "cause": "Deployment Failure",
        "confidence": 0.87,
        "peaks": (88.0, 79.0, 3200.0, 6.9, 156),
    },
    105: {
        "started_at": "2026-04-13T14:25:00",
        "component": "session-cache",
        "source": "Redis Monitor",
        "alert": "Session cache eviction rate increased sharply across the customer session cluster",
        "symptom": "A reduced maximum-memory setting forced active session keys out of the cache",
        "impact": "Customers experienced repeated authentication checks and unexpected session refreshes",
        "diagnosis": "A cache configuration change lowered available memory below the active working set",
        "mitigation": "The memory limit was restored and evicted sessions were warmed from the session store",
        "cause": "Application Failure",
        "confidence": 0.84,
        "peaks": (77.0, 87.0, 2100.0, 5.2, 143),
    },
    106: {
        "started_at": "2026-04-24T06:40:00",
        "component": "service-dns",
        "source": "DNS Monitor",
        "alert": "Internal DNS lookups began failing intermittently in two application zones",
        "symptom": "Resolver traces showed packet loss between application nodes and the DNS service",
        "impact": "Service discovery calls timed out and delayed dependent API requests",
        "diagnosis": "A network policy update dropped fragmented UDP responses from the DNS service",
        "mitigation": "The network policy was corrected and resolver caches were refreshed",
        "cause": "Network Issue",
        "confidence": 0.91,
        "peaks": (61.0, 58.0, 4600.0, 12.8, 95),
    },
    107: {
        "started_at": "2026-05-03T11:05:00",
        "component": "payment-callback-worker",
        "source": "Queue Monitor",
        "alert": "Payment callback queue depth exceeded the critical processing threshold",
        "symptom": "Worker concurrency remained fixed while callback traffic tripled",
        "impact": "Payment confirmations were delayed and order states remained pending",
        "diagnosis": "A worker autoscaling rule used the wrong queue-depth metric label",
        "mitigation": "The metric label was corrected and callback workers were scaled out",
        "cause": "Application Failure",
        "confidence": 0.88,
        "peaks": (86.0, 76.0, 3900.0, 8.0, 133),
    },
    108: {
        "started_at": "2026-05-16T08:30:00",
        "component": "search-indexer",
        "source": "Search Monitor",
        "alert": "Search index refresh jobs accumulated beyond the normal processing window",
        "symptom": "Indexer workers repeatedly retried a malformed catalog document batch",
        "impact": "New and updated catalog items were missing from customer search results",
        "diagnosis": "One malformed document caused the batch processor to retry the entire partition",
        "mitigation": "The document was quarantined and the failed index partitions were replayed",
        "cause": "Application Failure",
        "confidence": 0.82,
        "peaks": (91.0, 84.0, 1840.0, 3.9, 118),
    },
    109: {
        "started_at": "2026-05-28T17:15:00",
        "component": "order-event-consumer",
        "source": "Kafka Monitor",
        "alert": "Order event consumer lag increased across all checkout partitions",
        "symptom": "A poison event caused repeated retries and blocked partition progress",
        "impact": "Order fulfillment updates and customer notifications were delayed",
        "diagnosis": "The consumer lacked a dead-letter path for schema-incompatible events",
        "mitigation": "The event was moved to quarantine and a dead-letter rule was enabled",
        "cause": "Application Failure",
        "confidence": 0.85,
        "peaks": (78.0, 70.0, 2200.0, 2.8, 104),
    },
    110: {
        "started_at": "2026-06-07T03:50:00",
        "component": "primary-database-replica",
        "source": "Database Monitor",
        "alert": "Primary database replica lag exceeded the recovery point objective",
        "symptom": "A long-running reporting query consumed replica I/O capacity",
        "impact": "Read-after-write requests returned stale inventory and order information",
        "diagnosis": "Reporting traffic was routed to the transactional replica without workload limits",
        "mitigation": "The query was terminated and reporting traffic was moved to the analytics replica",
        "cause": "Database Issue",
        "confidence": 0.94,
        "peaks": (83.0, 81.0, 4100.0, 9.4, 220),
    },
    111: {
        "started_at": "2026-06-18T12:20:00",
        "component": "authentication-service",
        "source": "Identity APM",
        "alert": "Authentication error rate spiked after the identity service release",
        "symptom": "Token validation rejected keys loaded from the previous signing-key cache",
        "impact": "Valid users received authentication failures across web and mobile channels",
        "diagnosis": "The release did not invalidate cached signing keys during rotation",
        "mitigation": "The release was rolled back and signing-key caches were refreshed",
        "cause": "Deployment Failure",
        "confidence": 0.90,
        "peaks": (92.0, 78.0, 2450.0, 14.2, 172),
    },
    112: {
        "started_at": "2026-06-27T19:05:00",
        "component": "notification-queue",
        "source": "Queue Monitor",
        "alert": "Notification queue depth and message age crossed critical thresholds",
        "symptom": "Email provider throttling reduced consumer throughput below the incoming rate",
        "impact": "Transactional email and alert notifications were delivered late",
        "diagnosis": "Consumers retried throttled messages without exponential backoff",
        "mitigation": "Backoff was enabled and workers were rebalanced across provider routes",
        "cause": "Application Failure",
        "confidence": 0.88,
        "peaks": (87.0, 82.0, 3100.0, 7.6, 146),
    },
    113: {
        "started_at": "2026-07-05T07:45:00",
        "component": "checkout-service",
        "source": "Kubernetes",
        "alert": "Checkout pods repeatedly failed readiness checks after a configuration deployment",
        "symptom": "The readiness probe targeted a health endpoint removed by the new service version",
        "impact": "Load balancing capacity dropped and checkout requests returned 503 responses",
        "diagnosis": "Deployment configuration referenced an obsolete readiness endpoint",
        "mitigation": "The probe path was corrected and checkout pods were rolled out again",
        "cause": "Deployment Failure",
        "confidence": 0.93,
        "peaks": (80.0, 75.0, 3800.0, 18.0, 128),
    },
    114: {
        "started_at": "2026-07-17T15:30:00",
        "component": "inventory-sync-worker",
        "source": "Workflow Monitor",
        "alert": "Inventory synchronization duration exceeded the operational SLA",
        "symptom": "Workers serialized warehouse updates that could safely run in parallel",
        "impact": "Available stock counts were delayed across storefront channels",
        "diagnosis": "A feature flag disabled partitioned processing for warehouse updates",
        "mitigation": "Partitioned processing was restored and delayed updates were replayed",
        "cause": "Application Failure",
        "confidence": 0.86,
        "peaks": (79.0, 74.0, 2300.0, 4.7, 121),
    },
    115: {
        "started_at": "2026-07-29T21:10:00",
        "component": "reporting-worker",
        "source": "Heap Monitor",
        "alert": "Reporting worker memory usage grew throughout a large historical export",
        "symptom": "Completed report pages remained referenced until the full export finished",
        "impact": "Scheduled reports slowed and two export workers were terminated by memory limits",
        "diagnosis": "The export pipeline retained page buffers instead of streaming them to storage",
        "mitigation": "Exports were switched to streaming mode and affected workers were restarted",
        "cause": "Memory Leak",
        "confidence": 0.92,
        "peaks": (76.0, 96.0, 1650.0, 3.2, 88),
    },
}


def _seed_investigation_profiles(session: Session) -> None:
    incident_ids = set(DEFAULT_INVESTIGATION_PROFILES)
    incidents_by_id = {
        incident.id: incident
        for incident in session.scalars(select(Incident).where(Incident.id.in_(incident_ids))).all()
    }
    timeline_keys = {
        (item.incident_id, item.event_time, item.event_type)
        for item in session.scalars(select(Timeline).where(Timeline.incident_id.in_(incident_ids))).all()
    }
    metric_keys = {
        (item.incident_id, item.captured_at)
        for item in session.scalars(select(Metric).where(Metric.incident_id.in_(incident_ids))).all()
    }
    log_keys = {
        (item.incident_id, item.file_name)
        for item in session.scalars(select(Log).where(Log.incident_id.in_(incident_ids))).all()
    }
    prediction_incidents = set(
        session.scalars(select(Prediction.incident_id).where(Prediction.incident_id.in_(incident_ids))).all()
    )

    event_offsets = [0, 3, 7, 10, 15, 22]
    metric_curve = [0.48, 0.68, 0.90, 1.0, 0.74, 0.52]

    for incident_id, profile in DEFAULT_INVESTIGATION_PROFILES.items():
        incident = incidents_by_id.get(incident_id)
        if not incident:
            continue

        started_at = datetime.fromisoformat(profile["started_at"])
        events = [
            ("Alert", profile["alert"], profile["source"]),
            ("Correlation", profile["symptom"], "Telemetry Correlation"),
            ("Impact", profile["impact"], "APM"),
            ("Diagnosis", profile["diagnosis"], "Investigation"),
            ("Mitigation", profile["mitigation"], "Operations"),
            ("Recovery", f"Monitoring confirmed {profile['component']} returned to its expected operating range", "Monitoring"),
        ]
        for offset, (event_type, description, source) in zip(event_offsets, events):
            event_time = started_at + timedelta(minutes=offset)
            key = (incident_id, event_time, event_type)
            if key not in timeline_keys:
                session.add(
                    Timeline(
                        incident_id=incident_id,
                        event_time=event_time,
                        event_type=event_type,
                        description=description,
                        source=source,
                    )
                )

        peak_cpu, peak_memory, peak_response, peak_error, peak_connections = profile["peaks"]
        for offset, ratio in zip(event_offsets, metric_curve):
            captured_at = started_at + timedelta(minutes=offset)
            key = (incident_id, captured_at)
            if key not in metric_keys:
                session.add(
                    Metric(
                        incident_id=incident_id,
                        captured_at=captured_at,
                        cpu_usage=round(max(28.0, peak_cpu * ratio), 2),
                        memory_usage=round(max(38.0, peak_memory * ratio), 2),
                        disk_usage=round(48.0 + (offset * 0.25), 2),
                        response_time_ms=round(max(180.0, peak_response * ratio), 2),
                        error_rate=round(max(0.1, peak_error * ratio), 3),
                        database_connections=max(24, round(peak_connections * ratio)),
                    )
                )

        safe_component = profile["component"].replace("-", "_")
        log_records = [
            {
                "file_name": f"{safe_component}-events.log",
                "uploaded_at": started_at + timedelta(minutes=17),
                "parsed_content": (
                    f"{started_at:%H:%M:%S} WARN  {profile['alert']}\n"
                    f"{started_at + timedelta(minutes=7):%H:%M:%S} ERROR {profile['impact']}\n"
                    f"{started_at + timedelta(minutes=15):%H:%M:%S} INFO  {profile['mitigation']}"
                ),
            },
            {
                "file_name": f"{safe_component}-telemetry.log",
                "uploaded_at": started_at + timedelta(minutes=18),
                "parsed_content": (
                    f"component={profile['component']} peak_cpu={peak_cpu}% peak_memory={peak_memory}%\n"
                    f"peak_response_ms={peak_response} peak_error_rate={peak_error}% "
                    f"peak_db_connections={peak_connections}\n"
                    f"root_cause_candidate={profile['cause']} confidence={round(profile['confidence'] * 100)}%"
                ),
            },
        ]
        for log_record in log_records:
            key = (incident_id, log_record["file_name"])
            if key not in log_keys:
                session.add(
                    Log(
                        incident_id=incident_id,
                        file_name=log_record["file_name"],
                        file_type="LOG",
                        storage_path=f"uploads/seed/{log_record['file_name']}",
                        parsed_content=log_record["parsed_content"],
                        uploaded_at=log_record["uploaded_at"],
                    )
                )

        if incident_id not in prediction_incidents:
            session.add(
                Prediction(
                    incident_id=incident_id,
                    predicted_cause=profile["cause"],
                    confidence_score=profile["confidence"],
                    model_version="dt-v1.0.0",
                    predicted_at=started_at + timedelta(minutes=12),
                    model_features={
                        "priority": incident.priority,
                        "impact": incident.impact,
                        "urgency": incident.urgency,
                        "component": profile["component"],
                        "peak_response_time_ms": peak_response,
                        "peak_error_rate": peak_error,
                    },
                )
            )

def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_schema_upgrades()

    with Session(engine) as session:
        roles_by_name = {role.name: role for role in session.scalars(select(Role)).all()}
        for name, metadata in ROLES.items():
            role = roles_by_name.get(name)
            if role:
                role.description = metadata["description"]
                role.priority = metadata["priority"]
            else:
                role = Role(name=name, description=metadata["description"], priority=metadata["priority"])
                session.add(role)
                roles_by_name[name] = role

        permissions_by_code = {permission.code: permission for permission in session.scalars(select(Permission)).all()}
        for code, (module, description) in PERMISSIONS.items():
            permission = permissions_by_code.get(code)
            if permission:
                permission.module = module
                permission.description = description
            else:
                permission = Permission(code=code, module=module, description=description)
                session.add(permission)
                permissions_by_code[code] = permission

        session.flush()

        stale_permission_codes = set(permissions_by_code) & OBSOLETE_PERMISSIONS
        if stale_permission_codes:
            stale_permission_ids = [permissions_by_code[code].id for code in stale_permission_codes]
            session.execute(
                delete(RolePermission).where(RolePermission.permission_id.in_(stale_permission_ids))
            )
            session.execute(
                delete(Permission).where(Permission.id.in_(stale_permission_ids))
            )
            for code in stale_permission_codes:
                permissions_by_code.pop(code, None)
            session.flush()

        existing_links = {
            (link.role_id, link.permission_id)
            for link in session.scalars(select(RolePermission)).all()
        }
        desired_links: set[tuple[int, int]] = set()
        for role_name, permission_codes in ROLE_PERMISSIONS.items():
            role = roles_by_name[role_name]
            for permission_code in permission_codes:
                permission = permissions_by_code[permission_code]
                key = (role.id, permission.id)
                desired_links.add(key)
                if key not in existing_links:
                    session.add(RolePermission(role_id=role.id, permission_id=permission.id))

        managed_role_ids = {roles_by_name[role_name].id for role_name in ROLES}
        managed_permission_ids = {permission.id for permission in permissions_by_code.values()}
        for role_id, permission_id in existing_links - desired_links:
            if role_id in managed_role_ids and permission_id in managed_permission_ids:
                session.execute(
                    delete(RolePermission).where(
                        RolePermission.role_id == role_id,
                        RolePermission.permission_id == permission_id,
                    )
                )

        session.flush()

        users_by_email = {user.email: user for user in session.scalars(select(User)).all()}
        existing_user_roles = {
            (link.user_id, link.role_id)
            for link in session.scalars(select(UserRole)).all()
        }
        for full_name, email, role_name in DEFAULT_USERS:
            role = roles_by_name[role_name]
            user = users_by_email.get(email)
            if not user:
                user = User(
                    full_name=full_name,
                    email=email,
                    password_hash=hash_password(DEFAULT_USER_PASSWORD),
                    role_id=role.id,
                    is_active=True,
                )
                session.add(user)
                session.flush()
            else:
                if user.role_id != role.id:
                    user.role_id = role.id
                user.password_hash = hash_password(DEFAULT_USER_PASSWORD)
                user.is_active = True

            key = (user.id, role.id)
            if key not in existing_user_roles:
                session.add(UserRole(user_id=user.id, role_id=role.id))

        session.flush()

        users_by_email = {user.email: user for user in session.scalars(select(User)).all()}
        existing_incident_ids = set(session.scalars(select(Incident.id)).all())
        admin_user = users_by_email["admin@example.com"]
        for incident_data in DEFAULT_INCIDENTS:
            if incident_data["id"] in existing_incident_ids:
                continue
            assigned_user = users_by_email.get(incident_data["assigned_email"])
            session.add(
                Incident(
                    id=incident_data["id"],
                    incident_key=incident_data["incident_key"],
                    title=incident_data["title"],
                    description=incident_data["description"],
                    priority=incident_data["priority"],
                    impact=incident_data["impact"],
                    urgency=incident_data["urgency"],
                    status=incident_data["status"],
                    assigned_user_id=assigned_user.id if assigned_user else None,
                    created_by_id=admin_user.id,
                )
            )

        session.flush()

        existing_timeline_keys = {
            (item.incident_id, item.event_time, item.event_type)
            for item in session.scalars(select(Timeline)).all()
        }
        for incident_id, event_time, event_type, description, source in DEFAULT_TIMELINE_EVENTS:
            parsed_time = datetime.fromisoformat(event_time)
            key = (incident_id, parsed_time, event_type)
            if key not in existing_timeline_keys:
                session.add(
                    Timeline(
                        incident_id=incident_id,
                        event_time=parsed_time,
                        event_type=event_type,
                        description=description,
                        source=source,
                    )
                )

        existing_metric_keys = {
            (item.incident_id, item.captured_at)
            for item in session.scalars(select(Metric)).all()
        }
        for incident_id, captured_at, cpu, memory, disk, response_time, error_rate, db_connections in DEFAULT_METRICS:
            parsed_time = datetime.fromisoformat(captured_at)
            key = (incident_id, parsed_time)
            if key not in existing_metric_keys:
                session.add(
                    Metric(
                        incident_id=incident_id,
                        captured_at=parsed_time,
                        cpu_usage=cpu,
                        memory_usage=memory,
                        disk_usage=disk,
                        response_time_ms=response_time,
                        error_rate=error_rate,
                        database_connections=db_connections,
                    )
                )

        existing_log_keys = {
            (item.incident_id, item.file_name)
            for item in session.scalars(select(Log)).all()
        }
        for log_data in DEFAULT_LOGS:
            key = (log_data["incident_id"], log_data["file_name"])
            if key not in existing_log_keys:
                session.add(
                    Log(
                        incident_id=log_data["incident_id"],
                        file_name=log_data["file_name"],
                        file_type=log_data["file_type"],
                        storage_path=log_data["storage_path"],
                        parsed_content=log_data["parsed_content"],
                        uploaded_at=datetime.fromisoformat(log_data["uploaded_at"]),
                    )
                )

        existing_prediction_incidents = set(session.scalars(select(Prediction.incident_id)).all())
        for prediction_data in DEFAULT_PREDICTIONS:
            if prediction_data["incident_id"] not in existing_prediction_incidents:
                session.add(Prediction(**prediction_data))

        _seed_investigation_profiles(session)

        for page_key, payload in DEFAULT_OPERATIONAL_PAGES.items():
            page = session.get(OperationalPage, page_key)
            if page:
                page.payload = payload
            else:
                session.add(OperationalPage(page_key=page_key, payload=payload))

        session.commit()


def _ensure_schema_upgrades() -> None:
    inspector = inspect(engine)
    if "roles" not in inspector.get_table_names():
        return

    role_columns = {column["name"] for column in inspector.get_columns("roles")}
    if "priority" not in role_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE roles ADD COLUMN priority INT NOT NULL DEFAULT 0"))
