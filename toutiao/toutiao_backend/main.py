from fastapi import FastAPI
from routers import news
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],     # 允许的请求方法
    allow_headers=["*"],     # 允许的请求头
)

# 根路由
@app.get("/")
async def root():
    return {"message": "Hello World"}

# 挂载路由/注册路由
app.include_router(news.router)

# 启动
# conda activate web_learn
# cd D:\app4\GitHub\FastApi_learn\toutiao\toutiao_backend
# uvicorn main:app --reload --host 127.0.0.1 --port 8000
