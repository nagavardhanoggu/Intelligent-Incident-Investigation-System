from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: int
    fullName: str
    email: EmailStr
    role: str
    status: str = "ACTIVE"
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    priority: int


class UserCreate(BaseModel):
    fullName: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str
    status: str = "ACTIVE"


class UserUpdate(BaseModel):
    fullName: str | None = Field(default=None, min_length=3, max_length=150)
    email: EmailStr | None = None
    role: str | None = None
    status: str | None = None


class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "Bearer"
    expiresIn: int
    user: UserResponse


class AccountSettingsResponse(BaseModel):
    emailAlerts: bool = True
    criticalOnly: bool = False
    weeklyDigest: bool = True
    browserPush: bool = True
    mfaEnabled: bool = True
    autoAssign: bool = False
    compactWorkspace: bool = True
    auditExports: bool = True
    jwtSessionExpiry: str = "2 hours"
    activeSessions: int = 1
    alertChannels: int = 4


class AccountSettingsUpdate(BaseModel):
    emailAlerts: bool
    criticalOnly: bool
    weeklyDigest: bool
    browserPush: bool
    mfaEnabled: bool
    autoAssign: bool
    compactWorkspace: bool
    auditExports: bool


class ChangePasswordRequest(BaseModel):
    currentPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=8, max_length=128)


class ProfileDetail(BaseModel):
    label: str
    value: str
    icon: str


class ProfileStat(BaseModel):
    label: str
    value: str


class ProfileActivity(BaseModel):
    title: str
    time: datetime
    icon: str


class AccountProfileResponse(BaseModel):
    user: UserResponse
    details: list[ProfileDetail] = Field(default_factory=list)
    stats: list[ProfileStat] = Field(default_factory=list)
    activity: list[ProfileActivity] = Field(default_factory=list)


class AccountProfileUpdate(BaseModel):
    fullName: str = Field(min_length=3, max_length=150)
    email: EmailStr


class ServiceKpi(BaseModel):
    label: str
    value: str
    helper: str
    icon: str


class ServiceHealthItem(BaseModel):
    name: str
    detail: str
    owner: str
    status: str
    icon: str


class ServiceDependency(BaseModel):
    title: str
    detail: str


class ServiceHealthResponse(BaseModel):
    kpis: list[ServiceKpi] = Field(default_factory=list)
    services: list[ServiceHealthItem] = Field(default_factory=list)
    dependencies: list[ServiceDependency] = Field(default_factory=list)


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    priority: str
    impact: str
    urgency: str
    assignedUserId: int | None = None


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    priority: str | None = None
    impact: str | None = None
    urgency: str | None = None
    status: str | None = None
    assignedUserId: int | None = None
    finalRootCause: str | None = None


class IncidentResponse(BaseModel):
    id: int
    incidentKey: str
    title: str
    description: str | None
    priority: str
    impact: str
    urgency: str
    status: str
    assignedUser: str | None = None
    createdAt: datetime
    updatedAt: datetime


class MetricCreate(BaseModel):
    incidentId: int
    cpuUsage: float | None = Field(default=None, ge=0, le=100)
    memoryUsage: float | None = Field(default=None, ge=0, le=100)
    diskUsage: float | None = Field(default=None, ge=0, le=100)
    responseTimeMs: float | None = Field(default=None, ge=0)
    errorRate: float | None = Field(default=None, ge=0)
    databaseConnections: int | None = Field(default=None, ge=0)
    capturedAt: datetime


class MetricResponse(MetricCreate):
    id: int


class LogResponse(BaseModel):
    id: int
    incidentId: int
    fileName: str
    fileType: str
    storagePath: str
    uploadedAt: datetime
    parsedContent: str | None = None


class PredictRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    incidentId: int | None = None
    priority: str
    impact: str
    urgency: str
    reassignmentCount: int = Field(ge=0, alias="reassignment_count")
    reopenCount: int = Field(ge=0, alias="reopen_count")
    slaStatus: str = Field(alias="sla_status")
    category: str | None = "UNKNOWN"
    subcategory: str | None = "UNKNOWN"
    uSymptom: str | None = Field(default="UNKNOWN", alias="u_symptom")
    assignmentGroup: str | None = Field(default="UNKNOWN", alias="assignment_group")
    contactType: str | None = Field(default="UNKNOWN", alias="contact_type")
    knowledge: str | None = "UNKNOWN"
    sysModCount: int = Field(default=0, ge=0, alias="sys_mod_count")


class ProbableCause(BaseModel):
    cause: str
    probability: float


class PredictResponse(BaseModel):
    incidentId: int | None = None
    predictedCause: str
    confidenceScore: float
    modelVersion: str
    recommendedActions: list[str]
    topProbableCauses: list[ProbableCause] = Field(default_factory=list)
    keyDecisionFactors: list[str] = Field(default_factory=list)
    predictionTime: datetime


class InvestigationLogItem(LogResponse):
    parsedContent: str | None = None


class InvestigationTimelineItem(BaseModel):
    id: int
    eventTime: datetime
    eventType: str
    description: str
    source: str


class InvestigationMetricItem(BaseModel):
    id: int
    capturedAt: datetime
    cpuUsage: float | None = None
    memoryUsage: float | None = None
    diskUsage: float | None = None
    responseTimeMs: float | None = None
    errorRate: float | None = None
    databaseConnections: int | None = None


class InvestigationPredictionItem(BaseModel):
    id: int
    predictedCause: str
    confidenceScore: float
    modelVersion: str
    predictedAt: datetime
    modelFeatures: dict


class InvestigationSummary(BaseModel):
    signalCount: int
    logCount: int
    metricCount: int
    timelineCount: int
    riskLevel: str


class InvestigationWorkspaceResponse(BaseModel):
    incident: IncidentResponse
    summary: InvestigationSummary
    timeline: list[InvestigationTimelineItem]
    metrics: list[InvestigationMetricItem]
    logs: list[InvestigationLogItem]
    prediction: InvestigationPredictionItem | None = None
    recommendedActions: list[str] = Field(default_factory=list)
    similarIncidentKeys: list[str] = Field(default_factory=list)


class ResolutionCreate(BaseModel):
    incidentId: int
    incidentTitle: str
    rootCause: str
    resolution: str
    preventionSteps: str | None = None


class ResolutionResponse(ResolutionCreate):
    id: int
    updatedAt: datetime


class ReportKpi(BaseModel):
    averageMttr: str
    slaCompliance: str
    repeatIncidents: int


class MonthlyReportRow(BaseModel):
    month: str
    incidents: int
    critical: int
    mttr: str
    sla: str


class ReportInsight(BaseModel):
    title: str
    detail: str
    severity: str
    icon: str


class ReportReviewItem(BaseModel):
    title: str
    detail: str


class ReportsResponse(BaseModel):
    kpis: ReportKpi
    rows: list[MonthlyReportRow] = Field(default_factory=list)
    insights: list[ReportInsight] = Field(default_factory=list)
    reviewItems: list[ReportReviewItem] = Field(default_factory=list)
