# database/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 使用 SQLite，文件保存在项目根目录下的 ./research.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./research.db"

# 连接引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # SQLite专用参数
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖注入：获取数据库会话，用于FastAPI的Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()