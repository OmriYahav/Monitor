from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

class DeviceType(str, Enum):
    firewall="firewall"; switch="switch"; access_point="access_point"; ups="ups"; server="server"; camera="camera"; printer="printer"; other="other"
class DeviceStatus(str, Enum):
    online="online"; offline="offline"; unknown="unknown"
class AlertStatus(str, Enum):
    open="open"; acknowledged="acknowledged"; resolved="resolved"
class Severity(str, Enum):
    info="info"; warning="warning"; critical="critical"

class DeviceBase(BaseModel):
    name: str
    ip_address: str
    type: DeviceType
    vendor: str | None = None
    model: str | None = None
    site: str | None = None
    role: str | None = None
    enabled: bool = True
    polling_interval_seconds: int = Field(default=60, ge=10)

class DeviceCreate(DeviceBase): pass
class DeviceUpdate(BaseModel):
    name: str | None = None; ip_address: str | None = None; type: DeviceType | None = None
    vendor: str | None = None; model: str | None = None; site: str | None = None; role: str | None = None
    enabled: bool | None = None; polling_interval_seconds: int | None = Field(default=None, ge=10)

class DeviceRead(DeviceBase):
    id: UUID; status: DeviceStatus; last_seen: datetime | None; last_check: datetime | None; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}

class DeviceCheckRead(BaseModel):
    id: UUID; device_id: UUID; checked_at: datetime; success: bool; latency_ms: float | None; error_message: str | None
    model_config = {"from_attributes": True}

class AlertRead(BaseModel):
    id: UUID; device_id: UUID; severity: Severity; status: AlertStatus; title: str; message: str; started_at: datetime; resolved_at: datetime | None; acknowledged_at: datetime | None
    device: DeviceRead | None = None
    model_config = {"from_attributes": True}

class DashboardSummary(BaseModel):
    total_devices: int; online_devices: int; offline_devices: int; unknown_devices: int; open_alerts_count: int
    recent_alerts: list[AlertRead]; offline_devices_list: list[DeviceRead]
