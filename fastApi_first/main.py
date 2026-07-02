from fastapi import FastAPI,Path,Query;
from pydantic import BaseModel,Field;
from fastapi.responses import HTMLResponse;
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World3344"}

@app.get('/hello')
async def get_hello():
    return {"msg":"get_hello"}

# 使用Path函数控制传参
@app.get('/book/{id}')
async def get_book(id: int = Path(...,gt=0,lt=101,description="书籍ID,范围1-100")):
    return  {
        "id":id,
        "msg":"get_book"
    }

# 查找书籍作者,长度范围2-10
@app.get('/author/{name}')
async def get_author(name: str=Path(...,min_length=2,max_length=10,description="作者名称111")):
    return {
        "name":name,
        "msg":"get_author"
    }


# 查询参数 ， -》分页 ，limit： 返回记录数 10
@app.get('/news/news_list')
async def get_news_news(
        skip:int = Query(0,gt=0,description="跳过记录数"),
        limit:int =10
):
    return {
        "skip":skip,
        "limit":limit,
        "msg":"get_news_news"
    }


#08 请求体和响应体
# 请求体
class User(BaseModel):
    username:str = Field(...,min_length=2,max_length=10 ,description="用户名")
    password:str = Field(...,min_length=2,max_length=10,description="密码")

@app.post('/user/register')
async def user_register(user:User):
    return {
        "user":user,
        "msg":"user_register"
    }

# 11 Html返回类型
@app.get('/html',response_class=HTMLResponse)
async def get_html():
    return """
    <html>
        <head>
            <title>FastAPI</title>
        </head>
        <body>
            <h1>FastAPI</h1>
        </body>
    </html>
    """