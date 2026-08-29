CREATE TABLE IF NOT EXISTS roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id BIGINT NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id),
    INDEX idx_users_role_id (role_id),
    INDEX idx_users_active (is_active)
);

CREATE TABLE IF NOT EXISTS incidents (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    incident_key VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL,
    impact ENUM('LOW','MEDIUM','HIGH') NOT NULL,
    urgency ENUM('LOW','MEDIUM','HIGH') NOT NULL,
    status ENUM('OPEN','INVESTIGATING','RESOLVED','CLOSED') NOT NULL DEFAULT 'OPEN',
    assigned_user_id BIGINT NULL,
    created_by_id BIGINT NOT NULL,
    reassignment_count INT NOT NULL DEFAULT 0,
    reopen_count INT NOT NULL DEFAULT 0,
    sla_status ENUM('WITHIN_SLA','BREACHED','AT_RISK') NOT NULL DEFAULT 'WITHIN_SLA',
    final_root_cause VARCHAR(120),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at DATETIME NULL,
    CONSTRAINT fk_incidents_assigned_user FOREIGN KEY (assigned_user_id) REFERENCES users(id),
    CONSTRAINT fk_incidents_created_by FOREIGN KEY (created_by_id) REFERENCES users(id),
    INDEX idx_incidents_status_priority (status, priority),
    INDEX idx_incidents_created_at (created_at),
    FULLTEXT INDEX ft_incidents_title_desc (title, description)
);

CREATE TABLE IF NOT EXISTS logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    incident_id BIGINT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type ENUM('TXT','LOG','CSV') NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    parsed_content LONGTEXT,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_logs_incident FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE,
    INDEX idx_logs_incident_uploaded (incident_id, uploaded_at),
    FULLTEXT INDEX ft_logs_content (parsed_content)
);

CREATE TABLE IF NOT EXISTS metrics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    incident_id BIGINT NOT NULL,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    response_time_ms DECIMAL(10,2),
    error_rate DECIMAL(6,3),
    database_connections INT,
    captured_at DATETIME NOT NULL,
    CONSTRAINT fk_metrics_incident FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE,
    INDEX idx_metrics_incident_time (incident_id, captured_at)
);

CREATE TABLE IF NOT EXISTS timelines (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    incident_id BIGINT NOT NULL,
    event_time DATETIME NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    description TEXT NOT NULL,
    source VARCHAR(80) NOT NULL,
    CONSTRAINT fk_timelines_incident FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE,
    INDEX idx_timelines_incident_time (incident_id, event_time)
);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    incident_id BIGINT NOT NULL,
    predicted_cause ENUM('Deployment Failure','Database Issue','Network Issue','Memory Leak','Application Failure') NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    model_features JSON NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    predicted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_predictions_incident FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE,
    INDEX idx_predictions_incident_time (incident_id, predicted_at)
);

CREATE TABLE IF NOT EXISTS resolutions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    incident_id BIGINT NOT NULL,
    authored_by_id BIGINT NOT NULL,
    incident_title VARCHAR(255) NOT NULL,
    root_cause VARCHAR(120) NOT NULL,
    resolution TEXT NOT NULL,
    prevention_steps TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_resolutions_incident FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE,
    CONSTRAINT fk_resolutions_author FOREIGN KEY (authored_by_id) REFERENCES users(id),
    INDEX idx_resolutions_root_cause (root_cause),
    FULLTEXT INDEX ft_resolutions_search (incident_title, root_cause, resolution, prevention_steps)
);

INSERT IGNORE INTO roles (id, name, description) VALUES
  (1, 'ADMIN', 'System administrator'),
  (2, 'INVESTIGATOR', 'Incident investigator'),
  (3, 'VIEWER', 'Read-only dashboard and incident viewer');
