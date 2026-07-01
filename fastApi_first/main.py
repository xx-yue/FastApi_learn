from fastapi import FastAPI;
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/hello')
async def get_hello():
    return {"msg":"get_hello"}

