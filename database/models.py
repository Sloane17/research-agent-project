# database/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

# 用户表
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(128))
    email = Column(String(100), nullable=True)  # nullable=True 表示可以为空
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联：一个用户有多个研究任务
    tasks = relationship("ResearchTask", back_populates="owner")

# 研究任务表
class ResearchTask(Base):
    __tablename__ = "research_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))           # 用户输入的初始问题
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    final_report = Column(Text, nullable=True)      # 最终生成的 Markdown 报告
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)