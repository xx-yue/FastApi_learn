from fastapi import FastAPI,Path;

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


