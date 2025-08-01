from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text,
    JSON, Enum, Boolean, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    viewer = "viewer"
# Inside the User class in models.py
# ... (imports) ...

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    plan = Column(String, default="free")
    token_usage_this_month = Column(Integer, default=0)
    provider = Column(String, nullable=True)

    # --- THIS IS THE FIX ---
    # Add the fields needed for Stripe integration
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    # --- END OF FIX ---

    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("UserIntegration", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", cascade="all, delete-orphan")

# ... (rest of the file is the same)
    # ... (rest of AuditLog model)
class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    system_prompt = Column(Text, nullable=False)
    tools = Column(JSON, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="agents")
    chat_history = relationship("ChatMessage", back_populates="agent")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    response_time_seconds = Column(Numeric(10, 4), nullable=True)
    tool_calls = Column(JSON, nullable=True)
    token_usage = Column(JSON, nullable=True)

    agent = relationship("Agent", back_populates="chat_history")
    user = relationship("User", back_populates="messages")

class Tool(Base):
    __tablename__ = "tools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    function_name = Column(String, unique=True, nullable=False)
    is_public = Column(Boolean, default=True)



# Also, ensure the AuditLog model knows it has a ForeignKey relationship
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    # --- ENSURE THIS LINE IS A ForeignKey ---
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    action = Column(String, index=True, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")  # ✅ back_populates added

class UserIntegration(Base):
    __tablename__ = "user_integrations"
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False)
    encrypted_token = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="integrations")
