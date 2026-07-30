import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy import DateTime, func, String, Float, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel

# 加载 .env 文件（向上找到项目根目录的 .env）
load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI()


# 1. 创建异步引擎
# ASYNC_DATABASE_URL='mysql+aiomysql://root:o88o88@localhost:3306/fast_first?charset=utf8mb4'
ASYNC_DATABASE_URL=os.getenv("ASYNC_DATABASE_URL")
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 可选，输出 SQL 日志
    pool_size=10,  # 设置连接池活跃的连接数
    max_overflow=20,  # 允许额外的连接数
    pool_pre_ping=True,  # 每次从连接池取连接时先检测连接是否有效
    pool_recycle=3600,  # 连接回收时间（秒），避免 MySQL 8小时超时断开
)


# 2. 定义模型类： 基类 + 表对应的模型类
# 基类：创建时间、更新时间；书籍表：id、书名、作者、价格、出版社
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now, onupdate=func.now(), comment="修改时间")

# 创建新的表
class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍id")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")


# 3. 建表：定义函数建表 → FastAPI 启动的时候调用建表的函数
async def create_tables():
    # 获取异步引擎，创建事务 - 建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Base 模型类的元数据创建


# @app.on_event("startup")
# async def startup_event():
#     await create_tables()


@app.get("/")
async def root():
    return {"message": os.getenv("ASYNC_DATABASE_URL")}



AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  # 绑定数据库引擎
    class_=AsyncSession,  # 指定会话类
    expire_on_commit=False  # 提交后会话不过期，不会重新查询数据库
)


# 依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session  # 返回数据库会话给路由处理函数
            await session.commit()  # 提交事务
        except Exception:
            await session.rollback()  # 有异常，回滚
            raise
        finally:
            await session.close()  # 关闭会话

@app.get("/book/books")
async def get_book_list(db: AsyncSession = Depends(get_database)):
    # result = await db.execute(select(Book))  # 查询 → 返回一个 ORM 对象
    # book = result.scalars().all()  # 获取所有
    # book = result.scalars().first()  # 获取第一个
    book = await db.get(Book, 5)  # 获取单条数据 → 根据主键
    return book

# 需求：路径参数 书籍id
@app.get("/book/get_book/{book_id}")
async def get_book_list(book_id: int, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    return book


# 需求：条件 价格大于等于200
@app.get("/book/search_book")
async def get_search_book(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.price >= 200))
    books = result.scalars().all()
    return books



@app.get("/book/search_book")
async def get_search_book(db: AsyncSession = Depends(get_database)):
    # 需求： 作者以 曹 开头  % _
    # like() 模糊查询： % 任意个字符；_ 一个单个字符
    # result = await db.execute(select(Book).where(Book.author.like("曹_")))

    # & | ~ 与非
    # result = await db.execute(select(Book).where((Book.author.like("曹%")) | (Book.price > 100)))

    # in_() 包含
    # 需求：书籍id列表，数据库里面的 id 如果在 书籍id列表里面 就返回
    id_list = [1, 3, 5, 7]
    result = await db.execute(select(Book).where(Book.id.in_(id_list)))
    book = result.scalars().all()
    return book


#23 聚合函数
@app.get("/book/count")
async def get_count(db: AsyncSession = Depends(get_database)):
    # 聚合查询 select( func.方法名(模型类.属性) )
    # result = await db.execute(select(func.count(Book.id)))
    # result = await db.execute(select(func.max(Book.price)))
    # result = await db.execute(select(func.sum(Book.price)))
    result = await db.execute(select(func.avg(Book.price)))
    num = result.scalar()  # 用来提取一个数值 → 标量值
    return num


# 24分页查询
@app.get("/book/get_book_list")
async def get_book_list(
    page: int = 1,
    page_size: int = 3,
    db: AsyncSession = Depends(get_database)
):
    # （页码 - 1） * 每页数量
    skip = (page - 1) * page_size

    # offset 跳过的记录数  ； limit 每页的记录数
    stmt = select(Book).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books


# 25 需求：用户输入图书信息（id、书名、作者、价格、出版社） → 新增
# 用户输入 → 参数 → 请求体
class BookBase(BaseModel):
    id: int
    bookname: str
    author: str
    price: float
    publisher: str
@app.post("/book/add_book")
async def add_book(book: BookBase, db: AsyncSession = Depends(get_database)):
    # ORM对象 → add → commit
    book_obj = Book(**book.__dict__)
    db.add(book_obj)
    await db.commit()
    return book


# 26 需求：修改图书信息：先查再改
# 设计思路：路径参数书籍id：作用是查找；请求体参数：作用是新数据（书名、作者、价格、出版社）
class BookUpdate(BaseModel):
    bookname: str
    author: str
    price: float
    publisher: str
@app.put("/book/update_book/{book_id}")
async def update_book(book_id: int, data: BookUpdate, db: AsyncSession = Depends(get_database)):
    # 1. 查找图书
    db_book = await db.get(Book, book_id)

    # 如果未找到 抛出异常
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="查无此书"
        )

    # 2. 找到了则修改：重新赋值
    db_book.bookname = data.bookname
    db_book.author = data.author
    db_book.price = data.price
    db_book.publisher = data.publisher

    # 3. 提交到数据库
    await db.commit()
    return db_book


# 28 删除图书
@app.delete("/book/delete_book/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_database)):
    # 先查再删 提交
    db_book = await db.get(Book, book_id)

    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="查无此书"
        )

    await db.delete(db_book)
    await db.commit()
    return {"msg": "删除图书成功"}