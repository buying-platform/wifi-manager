from pydantic import BaseModel
from typing import Optional


# ─── Auth ───
class LoginRequest(BaseModel):
    user_id: str
    pin: str

class LoginResponse(BaseModel):
    token: str
    user_id: str
    name: str
    role: str


# ─── Settings ───
class Settings(BaseModel):
    id: int
    finance_email: str
    reminder_days: int
    currency: str
    season_label: str
    season_end_default: str
    class Config:
        from_attributes = True

class SettingsUpdate(BaseModel):
    finance_email: Optional[str] = None
    reminder_days: Optional[int] = None
    currency: Optional[str] = None
    season_label: Optional[str] = None
    season_end_default: Optional[str] = None


# ─── Provider ───
class ProviderCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class Provider(ProviderCreate):
    id: int
    class Config:
        from_attributes = True


# ─── Warehouse ───
class WarehouseCreate(BaseModel):
    code: str
    name: str
    address: Optional[str] = None
    provider_id: Optional[int] = None
    contact: Optional[str] = None
    notes: Optional[str] = None

class Warehouse(WarehouseCreate):
    id: int
    class Config:
        from_attributes = True


# ─── Subscription ───
class SubscriptionCreate(BaseModel):
    warehouse_id: int
    provider_id: int
    plan_type: str
    price: float
    currency: Optional[str] = "USD"
    expiry_date: Optional[str] = None
    pay_by_date: Optional[str] = None
    season_end_date: Optional[str] = None
    start_date: Optional[str] = None

class Subscription(SubscriptionCreate):
    id: int
    class Config:
        from_attributes = True
