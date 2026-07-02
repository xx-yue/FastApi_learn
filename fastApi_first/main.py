from fastapi import FastAPI,Path,Query;

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
@app.get('/news/newws_list')
async def get_news_news(
        skip:int = Query(0,gt=0,description="跳过记录数"),
        limit:int =10
):
    return {
        "skip":skip,
        "limit":limit,
        "msg":"get_news_news"
    }




