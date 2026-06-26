from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from database import Base
from datetime import datetime
import json


# =========================
# TEMPLATE
# =========================
class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# DESTINATION (GROUPS / CHANNELS)
# =========================
class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)

    # chat_id แนะนำสำหรับ Telegram (ถ้ามี)
    chat_id = Column(String(100), nullable=True)

    status = Column(String(50), default="active")

    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# JOB (SAAS PRO LEVEL)
# =========================
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    # basic info
    title = Column(String(255), nullable=True)

    template_id = Column(Integer, nullable=False)

    # multi-group system (JSON list)
    destination_ids = Column(Text, nullable=False)
    # example: "[1,2,3]"

    schedule_time = Column(String(100), nullable=True)

    # =========================
    # STATUS SYSTEM
    # =========================
    status = Column(String(50), default="pending")
    # pending | running | completed | failed | stopped

    locked = Column(Boolean, default=False)

    # =========================
    # PROGRESS SYSTEM
    # =========================
    current_run = Column(Integer, default=0)
    total_runs = Column(Integer, default=0)
    progress = Column(Integer, default=0)  # 0 - 100

    # =========================
    # RETRY SYSTEM
    # =========================
    retry_count = Column(Integer, default=0)
    max_retry = Column(Integer, default=3)

    # =========================
    # CONTROL
    # =========================
    is_repeatable = Column(Boolean, default=False)
    interval_seconds = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # =========================
    # HELPERS
    # =========================
    def get_destination_ids(self):
        try:
            return json.loads(self.destination_ids or "[]")
        except:
            return []