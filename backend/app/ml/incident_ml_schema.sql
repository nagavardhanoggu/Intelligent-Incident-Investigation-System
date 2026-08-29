CREATE TABLE IF NOT EXISTS incident_training_records (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  source_incident_id VARCHAR(80),
  priority VARCHAR(30) NOT NULL,
  impact VARCHAR(30) NOT NULL,
  urgency VARCHAR(30) NOT NULL,
  reassignment_count INT NOT NULL DEFAULT 0,
  reopen_count INT NOT NULL DEFAULT 0,
  made_sla TINYINT(1) NOT NULL DEFAULT 1,
  root_cause VARCHAR(120) NOT NULL,
  incident_state VARCHAR(120),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_training_root_cause (root_cause),
  INDEX idx_training_priority (priority),
  INDEX idx_training_sla (made_sla)
);

CREATE TABLE IF NOT EXISTS incident_predictions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  incident_id BIGINT NOT NULL,
  priority VARCHAR(30) NOT NULL,
  impact VARCHAR(30) NOT NULL,
  urgency VARCHAR(30) NOT NULL,
  reassignment_count INT NOT NULL DEFAULT 0,
  reopen_count INT NOT NULL DEFAULT 0,
  made_sla TINYINT(1) NOT NULL DEFAULT 1,
  predicted_cause VARCHAR(120) NOT NULL,
  confidence_score DECIMAL(6, 2) NOT NULL,
  model_version VARCHAR(80) NOT NULL,
  predicted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_prediction_incident (incident_id),
  INDEX idx_prediction_cause (predicted_cause),
  INDEX idx_prediction_date (predicted_at)
);
