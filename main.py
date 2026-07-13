# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Form  # 添加 , Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware

# 导入数据库模块
from database.database import get_db, engine, Base
from database.models import User, ResearchTask

# 导入认证模块
from backend.auth import (
    authenticate_user, 
    get_current_user, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware

# 导入数据库模块
from database.database import get_db, engine, Base
from database.models import User, ResearchTask

# 导入认证模块
from backend.auth import (
    authenticate_user, 
    get_current_user, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Research Agent API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/")
def read_root():
    return {"message": "Research Agent is Running"}

# ---- 用户注册接口 ----
@app.post("/api/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 加密密码并创建用户
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully", "user_id": new_user.id}

# ---- 用户登录接口 ----
@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ---- 获取当前用户信息 ----
@app.get("/api/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }
# main.py - 在文件末尾追加以下内容

from pydantic import BaseModel
from fastapi import BackgroundTasks
from ai_core.workflow import run_research_workflow

# 定义请求体格式
class ResearchRequest(BaseModel):
    query: str

# 启动研究任务（异步执行）
@app.post("/api/research/start")
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. 在数据库中创建任务记录
    new_task = ResearchTask(
        title=request.query,
        status="running",
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # 2. 定义后台执行的任务
    def run_task(task_id: int, query: str):
        # 重新获取数据库会话（后台任务需要独立的会话）
        from database.database import SessionLocal
        db_local = SessionLocal()
        try:
            # 执行研究工作流
            report = run_research_workflow(query)
            
            # 更新任务状态
            task = db_local.query(ResearchTask).filter(ResearchTask.id == task_id).first()
            if task:
                task.status = "completed"
                task.final_report = report
                db_local.commit()
                print(f"✅ 任务 {task_id} 完成！")
        except Exception as e:
            task = db_local.query(ResearchTask).filter(ResearchTask.id == task_id).first()
            if task:
                task.status = "failed"
                db_local.commit()
            print(f"❌ 任务 {task_id} 失败: {e}")
        finally:
            db_local.close()
    
    # 3. 将任务添加到后台队列
    background_tasks.add_task(run_task, new_task.id, request.query)
    
    return {
        "task_id": new_task.id,
        "status": "running",
        "message": "研究任务已启动，请稍后查询结果"
    }

# 查询任务状态和报告
@app.get("/api/research/status/{task_id}")
async def get_research_status(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    task = db.query(ResearchTask).filter(
        ResearchTask.id == task_id,
        ResearchTask.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 计算进度
    progress = 0
    if task.status == "pending":
        progress = 0
    elif task.status == "running":
        progress = 50  # 运行中显示 50%
    elif task.status == "completed":
        progress = 100
    elif task.status == "failed":
        progress = 0
    
    return {
        "task_id": task.id,
        "title": task.title,
        "status": task.status,
        "progress": progress,  # 新增进度字段
        "report": task.final_report if task.status == "completed" else None,
        "created_at": task.created_at
    }

# 获取用户的所有研究任务
@app.get("/api/research/tasks")
async def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(ResearchTask).filter(
        ResearchTask.user_id == current_user.id
    ).order_by(ResearchTask.created_at.desc()).all()
    
    return [
        {
            "task_id": task.id,
            "title": task.title,
            "status": task.status,
            "created_at": task.created_at
        }
        for task in tasks
    ]
# main.py - 在文件末尾添加

from fastapi.responses import StreamingResponse
import json
from ai_core.workflow import run_research_workflow_stream

@app.post("/api/research/stream")
async def research_stream(
    request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """流式研究接口 - 实时推送进度"""
    
    from ai_core.workflow import run_research_workflow_stream
    
    # 创建任务记录
    new_task = ResearchTask(
        title=request.query,
        status="running",
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    async def generate():
        try:
            # 发送任务 ID
            yield f"data: {json.dumps({'type': 'task_id', 'task_id': new_task.id})}\n\n"
            
            # 执行研究工作流，逐步推送
            for event in run_research_workflow_stream(request.query):
                yield f"data: {json.dumps(event)}\n\n"
                
            # 任务完成后更新数据库
            task = db.query(ResearchTask).filter(ResearchTask.id == new_task.id).first()
            if task:
                # 从事件中获取最终报告
                # 这里简化处理，直接从 workflow 获取
                task.status = "completed"
                db.commit()
                
        except Exception as e:
            # 更新任务状态为失败
            task = db.query(ResearchTask).filter(ResearchTask.id == new_task.id).first()
            if task:
                task.status = "failed"
                db.commit()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

# main.py - 在文件末尾添加

from fastapi import BackgroundTasks

class ResearchRequest(BaseModel):
    query: str

@app.post("/api/research/start")
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交研究任务（非流式）"""
    
    # 1. 创建任务记录
    new_task = ResearchTask(
        title=request.query,
        status="running",
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # 2. 定义后台执行的任务
    def run_task(task_id: int, query: str):
        from database.database import SessionLocal
        from ai_core.workflow import run_research_workflow
        
        db_local = SessionLocal()
        try:
            # 执行 AI 研究
            report = run_research_workflow(query)
            
            # 更新任务状态
            task = db_local.query(ResearchTask).filter(ResearchTask.id == task_id).first()
            if task:
                task.status = "completed"
                task.final_report = report
                db_local.commit()
                print(f"✅ 任务 {task_id} 完成！")
        except Exception as e:
            task = db_local.query(ResearchTask).filter(ResearchTask.id == task_id).first()
            if task:
                task.status = "failed"
                db_local.commit()
            print(f"❌ 任务 {task_id} 失败: {e}")
        finally:
            db_local.close()
    
    # 3. 将任务放入后台执行
    background_tasks.add_task(run_task, new_task.id, request.query)
    
    return {
        "task_id": new_task.id,
        "status": "running",
        "message": "研究任务已启动"
    }


@app.get("/api/research/status/{task_id}")
async def get_research_status(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询任务状态和报告"""
    
    task = db.query(ResearchTask).filter(
        ResearchTask.id == task_id,
        ResearchTask.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task.id,
        "title": task.title,
        "status": task.status,  # running / completed / failed
        "report": task.final_report if task.status == "completed" else None,
        "created_at": task.created_at
    }


@app.get("/api/research/tasks")
async def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有任务"""
    
    tasks = db.query(ResearchTask).filter(
        ResearchTask.user_id == current_user.id
    ).order_by(ResearchTask.created_at.desc()).all()
    
    return [
        {
            "task_id": task.id,
            "title": task.title,
            "status": task.status,
            "created_at": task.created_at
        }
        for task in tasks
    ]