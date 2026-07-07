from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class Role(str, Enum): admin="admin"; operator="operator"; viewer="viewer"
class DeviceType(str, Enum):
    firewall="firewall"; router="router"; switch="switch"; access_point="access_point"; ups="ups"; server="server"; camera="camera"; printer="printer"; controller="controller"; internet_uplink="internet_uplink"; vpn_tunnel="vpn_tunnel"; other="other"
class DeviceStatus(str, Enum): online="online"; offline="offline"; warning="warning"; unknown="unknown"; maintenance="maintenance"
class Criticality(str, Enum): low="low"; medium="medium"; high="high"; critical="critical"
class AlertStatus(str, Enum): open="open"; acknowledged="acknowledged"; resolved="resolved"
class Severity(str, Enum): info="info"; warning="warning"; high="high"; critical="critical"

class Token(BaseModel): access_token: str; token_type: str = "bearer"
class LoginRequest(BaseModel): email: EmailStr; password: str
class UserRead(BaseModel):
    id: UUID; name: str; email: EmailStr; role: Role; enabled: bool; created_at: datetime; updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
class UserCreate(BaseModel): name: str; email: EmailStr; password: str = Field(min_length=8); role: Role = Role.viewer; enabled: bool = True
class UserUpdate(BaseModel): name: str | None=None; email: EmailStr | None=None; password: str | None=Field(default=None, min_length=8); role: Role | None=None; enabled: bool | None=None

class SiteBase(BaseModel): name: str; description: str | None=None; address: str | None=None; timezone: str="UTC"
class SiteCreate(SiteBase): pass
class SiteUpdate(BaseModel): name: str | None=None; description: str | None=None; address: str | None=None; timezone: str | None=None
class SiteRead(SiteBase):
    id: UUID; created_at: datetime; updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DeviceBase(BaseModel):
    name: str; ip_address: str; type: DeviceType
    hostname: str | None=None; vendor: str | None=None; model: str | None=None; serial_number: str | None=None; firmware_version: str | None=None
    site_id: UUID | None=None; location: str | None=None; rack: str | None=None; role: str | None=None; criticality: Criticality=Criticality.medium
    enabled: bool=True; polling_interval_seconds: int=Field(default=60, ge=10); snmp_enabled: bool=False; snmp_profile_id: UUID | None=None; syslog_enabled: bool=False; notes: str | None=None
class DeviceCreate(DeviceBase): pass
class DeviceUpdate(BaseModel):
    name: str | None=None; ip_address: str | None=None; type: DeviceType | None=None; hostname: str | None=None; vendor: str | None=None; model: str | None=None; serial_number: str | None=None; firmware_version: str | None=None; site_id: UUID | None=None; location: str | None=None; rack: str | None=None; role: str | None=None; criticality: Criticality | None=None; enabled: bool | None=None; status: DeviceStatus | None=None; polling_interval_seconds: int | None=Field(default=None, ge=10); snmp_enabled: bool | None=None; snmp_profile_id: UUID | None=None; syslog_enabled: bool | None=None; notes: str | None=None
class DeviceRead(DeviceBase):
    id: UUID; status: DeviceStatus; last_seen: datetime | None; last_check: datetime | None; created_at: datetime; updated_at: datetime; site: SiteRead | None=None
    model_config = ConfigDict(from_attributes=True)

class DeviceCheckRead(BaseModel):
    id: UUID; device_id: UUID; checked_at: datetime; success: bool; latency_ms: float | None; error_message: str | None
    model_config = ConfigDict(from_attributes=True)
class AlertRead(BaseModel):
    id: UUID; device_id: UUID; severity: Severity; status: AlertStatus; title: str; message: str; metric_name: str | None=None; current_value: float | None=None; threshold: float | None=None; first_seen: datetime; last_seen: datetime; started_at: datetime; resolved_at: datetime | None; acknowledged_at: datetime | None; device: DeviceRead | None=None
    model_config = ConfigDict(from_attributes=True)
class AlertRuleRead(BaseModel):
    id: UUID; name: str; description: str | None; target_type: str; metric_name: str; condition: str; threshold: float | None; duration_seconds: int; severity: Severity; enabled: bool; created_at: datetime; updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
class AlertRuleCreate(BaseModel): name: str; description: str | None=None; target_type: str="device"; metric_name: str; condition: str; threshold: float | None=None; duration_seconds: int=60; severity: Severity=Severity.warning; enabled: bool=True
class SNMPProfileCreate(BaseModel): name: str; version: str="2c"; community: str | None=None; username: str | None=None; auth_protocol: str | None=None; auth_password: str | None=None; privacy_protocol: str | None=None; privacy_password: str | None=None; security_level: str | None=None; port: int=161; timeout_seconds: int=2; retries: int=1
class SNMPProfileRead(BaseModel):
    id: UUID; name: str; version: str; username: str | None; auth_protocol: str | None; privacy_protocol: str | None; security_level: str | None; port: int; timeout_seconds: int; retries: int; created_at: datetime; updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
class DashboardSummary(BaseModel):
    total_devices: int; online_devices: int; offline_devices: int; warning_devices: int; unknown_devices: int; open_alerts_count: int; recent_alerts: list[AlertRead]; offline_devices_list: list[DeviceRead]
