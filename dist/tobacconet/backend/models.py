from sqlalchemy import Column, Integer, String, Numeric, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Setting(Base):
    __tablename__ = "settings"
    id                  = Column(Integer, primary_key=True, default=1)
    finance_email       = Column(String(255), default="finance@tobaccoauction.co.zw")
    reminder_days       = Column(Integer, default=7)
    currency            = Column(String(10), default="USD")
    season_label        = Column(String(20), default="2025/2026")
    season_end_default  = Column(String(10), default="2026-06-30")


class Provider(Base):
    __tablename__ = "providers"
    id      = Column(Integer, primary_key=True, autoincrement=True)
    name    = Column(String(100), nullable=False)
    contact = Column(String(100))
    phone   = Column(String(50))
    email   = Column(String(150))
    website = Column(String(150))

    warehouses    = relationship("Warehouse",    back_populates="provider")
    subscriptions = relationship("Subscription", back_populates="provider")


class Warehouse(Base):
    __tablename__ = "warehouses"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    code        = Column(String(20), nullable=False, unique=True)
    name        = Column(String(150), nullable=False)
    address     = Column(String(255))
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    contact     = Column(String(150))
    notes       = Column(Text)

    provider      = relationship("Provider",     back_populates="warehouses")
    subscriptions = relationship("Subscription", back_populates="warehouse", cascade="all, delete-orphan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id     = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    provider_id      = Column(Integer, ForeignKey("providers.id"), nullable=False)
    plan_type        = Column(String(100), nullable=False)
    price            = Column(Numeric(10, 2), nullable=False, default=0)
    currency         = Column(String(10), default="USD")
    expiry_date      = Column(String(10))
    pay_by_date      = Column(String(10))
    season_end_date  = Column(String(10))
    start_date       = Column(String(10))

    warehouse = relationship("Warehouse", back_populates="subscriptions")
    provider  = relationship("Provider",  back_populates="subscriptions")
