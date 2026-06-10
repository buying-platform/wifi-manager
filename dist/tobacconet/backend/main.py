from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import os

from database import get_db, engine
from models import Base
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TobaccoNet API", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# In-memory session store: token -> user_id
sessions: dict[str, str] = {}

# ─── Users (hardcoded, PINs hashed in production but simple here) ───
USERS = {
    "jeremiah": {"name": "Jeremiah", "role": "Head Of IT",            "pin": "7392", "initials": "JM", "color": "#1a6635"},
    "obert":    {"name": "Obert",    "role": "IT Manager",            "pin": "4817", "initials": "OM", "color": "#185a80"},
    "lloyd":    {"name": "Lloyd",    "role": "IT Manager",            "pin": "6254", "initials": "LM", "color": "#6a3a8a"},
    "ryan":     {"name": "Ryan",     "role": "Chief Finance Officer", "pin": "9031", "initials": "RT", "color": "#8a4a1a"},
}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    user_id = sessions.get(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return {"id": user_id, **USERS[user_id]}


# ══════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════

@app.get("/api/users")
def list_users():
    """Return user list (no PINs) for the login screen."""
    return [
        {"id": uid, "name": u["name"], "role": u["role"],
         "initials": u["initials"], "color": u["color"]}
        for uid, u in USERS.items()
    ]


@app.post("/api/auth/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest):
    user = USERS.get(payload.user_id)
    if not user or user["pin"] != payload.pin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = secrets.token_urlsafe(32)
    sessions[token] = payload.user_id
    return {"token": token, "user_id": payload.user_id, "name": user["name"], "role": user["role"]}


@app.post("/api/auth/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        sessions.pop(credentials.credentials, None)
    return {"ok": True}


# ══════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════

@app.get("/api/settings", response_model=schemas.Settings)
def get_settings(db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Setting).first()
    if not row:
        row = models.Setting()
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@app.put("/api/settings", response_model=schemas.Settings)
def update_settings(payload: schemas.SettingsUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Setting).first()
    if not row:
        row = models.Setting()
        db.add(row)
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


# ══════════════════════════════════════════
#  PROVIDERS (ISPs)
# ══════════════════════════════════════════

@app.get("/api/providers", response_model=list[schemas.Provider])
def list_providers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Provider).order_by(models.Provider.name).all()


@app.post("/api/providers", response_model=schemas.Provider, status_code=201)
def create_provider(payload: schemas.ProviderCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = models.Provider(**payload.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.put("/api/providers/{id}", response_model=schemas.Provider)
def update_provider(id: int, payload: schemas.ProviderCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Provider).filter(models.Provider.id == id).first()
    if not row:
        raise HTTPException(404, "Provider not found")
    for k, v in payload.dict().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@app.delete("/api/providers/{id}")
def delete_provider(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Provider).filter(models.Provider.id == id).first()
    if not row:
        raise HTTPException(404, "Provider not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ══════════════════════════════════════════
#  WAREHOUSES
# ══════════════════════════════════════════

@app.get("/api/warehouses", response_model=list[schemas.Warehouse])
def list_warehouses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Warehouse).order_by(models.Warehouse.code).all()


@app.post("/api/warehouses", response_model=schemas.Warehouse, status_code=201)
def create_warehouse(payload: schemas.WarehouseCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = models.Warehouse(**payload.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.put("/api/warehouses/{id}", response_model=schemas.Warehouse)
def update_warehouse(id: int, payload: schemas.WarehouseCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Warehouse).filter(models.Warehouse.id == id).first()
    if not row:
        raise HTTPException(404, "Warehouse not found")
    for k, v in payload.dict().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@app.delete("/api/warehouses/{id}")
def delete_warehouse(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Warehouse).filter(models.Warehouse.id == id).first()
    if not row:
        raise HTTPException(404, "Warehouse not found")
    db.query(models.Subscription).filter(models.Subscription.warehouse_id == id).delete()
    db.delete(row)
    db.commit()
    return {"ok": True}


# ══════════════════════════════════════════
#  SUBSCRIPTIONS
# ══════════════════════════════════════════

@app.get("/api/subscriptions", response_model=list[schemas.Subscription])
def list_subscriptions(warehouse_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(models.Subscription)
    if warehouse_id:
        q = q.filter(models.Subscription.warehouse_id == warehouse_id)
    return q.order_by(models.Subscription.expiry_date).all()


@app.post("/api/subscriptions", response_model=schemas.Subscription, status_code=201)
def create_subscription(payload: schemas.SubscriptionCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = models.Subscription(**payload.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.put("/api/subscriptions/{id}", response_model=schemas.Subscription)
def update_subscription(id: int, payload: schemas.SubscriptionCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Subscription).filter(models.Subscription.id == id).first()
    if not row:
        raise HTTPException(404, "Subscription not found")
    for k, v in payload.dict().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@app.delete("/api/subscriptions/{id}")
def delete_subscription(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.query(models.Subscription).filter(models.Subscription.id == id).first()
    if not row:
        raise HTTPException(404, "Subscription not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ══════════════════════════════════════════
#  SEED ENDPOINT (first-run demo data)
# ══════════════════════════════════════════

@app.post("/api/seed")
def seed_data(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] != "Administrator":
        raise HTTPException(403, "Only administrators can seed data")
    if db.query(models.Warehouse).count() > 0:
        return {"ok": False, "message": "Data already exists"}

    p1 = models.Provider(name="TelOne Zimbabwe", contact="Sales Desk", phone="+263 4 700000", email="business@telone.co.zw", website="www.telone.co.zw")
    p2 = models.Provider(name="ZOL Zimbabwe", contact="Account Manager", phone="+263 77 800000", email="support@zol.co.zw", website="www.zol.co.zw")
    p3 = models.Provider(name="NetOne Business", contact="Corporate Sales", phone="+263 71 900000", email="corporate@netone.co.zw", website="www.netone.co.zw")
    db.add_all([p1, p2, p3]); db.flush()

    warehouses = [
        models.Warehouse(code="WH01", name="Central Auction Hall",     address="123 Tobacco Rd, Harare",           provider_id=p1.id, contact="T: +263 4 123456"),
        models.Warehouse(code="WH02", name="Northern Grading Shed",    address="45 Farm Rd, Bindura",              provider_id=p2.id, contact="T: +263 71 234567"),
        models.Warehouse(code="WH03", name="Eastern Storage Complex",  address="78 Mutare Rd, Mutare",             provider_id=p1.id, contact="T: +263 20 345678"),
        models.Warehouse(code="WH04", name="Southern Processing Unit", address="12 Beit Bridge Rd, Masvingo",      provider_id=p3.id, contact="T: +263 39 456789"),
        models.Warehouse(code="WH05", name="Western Weighbridge",      address="99 Bulawayo Ave, Bulawayo",        provider_id=p2.id, contact="T: +263 9 567890"),
        models.Warehouse(code="WH06", name="Karoi Grading Floor",      address="3 Karoi-Harare Rd, Karoi",         provider_id=p1.id, contact="T: +263 64 111222"),
        models.Warehouse(code="WH07", name="Mvurwi Auction Bay",       address="6 Main St, Mvurwi",                provider_id=p3.id, contact="T: +263 75 333444"),
        models.Warehouse(code="WH08", name="Chinhoyi Leaf Store",      address="21 Chirundu Rd, Chinhoyi",         provider_id=p2.id, contact="T: +263 67 555666"),
    ]
    db.add_all(warehouses); db.flush()
    wh = {w.code: w for w in warehouses}

    subs = [
        models.Subscription(warehouse_id=wh["WH01"].id, provider_id=p1.id, plan_type="Fibre 100Mbps",        price=180, expiry_date="2025-08-15", pay_by_date="2025-08-10", season_end_date="2026-06-30", start_date="2024-08-15"),
        models.Subscription(warehouse_id=wh["WH01"].id, provider_id=p1.id, plan_type="Backup LTE 10Mbps",    price=45,  expiry_date="2025-07-31", pay_by_date="2025-07-25", season_end_date="2026-06-30", start_date="2024-07-31"),
        models.Subscription(warehouse_id=wh["WH02"].id, provider_id=p2.id, plan_type="Fibre 50Mbps",         price=120, expiry_date="2025-09-01", pay_by_date="2025-08-26", season_end_date="2026-05-31", start_date="2024-09-01"),
        models.Subscription(warehouse_id=wh["WH03"].id, provider_id=p1.id, plan_type="VDSL 20Mbps",          price=85,  expiry_date="2025-08-20", pay_by_date="2025-08-15", season_end_date="2026-07-31", start_date="2024-08-20"),
        models.Subscription(warehouse_id=wh["WH04"].id, provider_id=p3.id, plan_type="LTE Business 30Mbps",  price=95,  expiry_date="2025-07-28", pay_by_date="2025-07-23", season_end_date="2026-06-15", start_date="2024-07-28"),
        models.Subscription(warehouse_id=wh["WH05"].id, provider_id=p2.id, plan_type="Fibre 100Mbps",        price=175, expiry_date="2025-09-10", pay_by_date="2025-09-05", season_end_date="2026-08-31", start_date="2024-09-10"),
        models.Subscription(warehouse_id=wh["WH06"].id, provider_id=p1.id, plan_type="ADSL 10Mbps",          price=55,  expiry_date="2025-08-05", pay_by_date="2025-07-31", season_end_date="2026-04-30", start_date="2024-08-05"),
        models.Subscription(warehouse_id=wh["WH07"].id, provider_id=p3.id, plan_type="LTE Business 20Mbps",  price=75,  expiry_date="2025-08-22", pay_by_date="2025-08-17", season_end_date="2026-05-31", start_date="2024-08-22"),
        models.Subscription(warehouse_id=wh["WH08"].id, provider_id=p2.id, plan_type="Fibre 50Mbps",         price=130, expiry_date="2025-09-15", pay_by_date="2025-09-10", season_end_date="2026-07-15", start_date="2024-09-15"),
        models.Subscription(warehouse_id=wh["WH02"].id, provider_id=p2.id, plan_type="Backup LTE 5Mbps",     price=35,  expiry_date="2025-08-01", pay_by_date="2025-07-27", season_end_date="2026-05-31", start_date="2024-08-01"),
    ]
    db.add_all(subs)
    db.commit()
    return {"ok": True, "message": "Demo data seeded successfully"}


@app.get("/")
def root():
    return {"service": "TobaccoNet API", "status": "running", "version": "1.0.0"}
