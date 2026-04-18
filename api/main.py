from fastapi import FastAPI, HTTPException, Depends, Request, Security, status
from fastapi.security import APIKeyHeader
from fastapi.responses import RedirectResponse
from utilities.database import book_collection, change_log_detection
from bson import ObjectId
import os 
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
load_dotenv()
valid_api_key = os.getenv("API_KEY")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == valid_api_key:
        return api_key
    raise HTTPException(
        status_code= status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

app = FastAPI(dependencies=[Depends(get_api_key)])


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/", dependencies=[])

async def redirect_to_docs():
    return RedirectResponse(url="/docs")


from fastapi import Query
from typing import Optional

@app.get("/books")
@limiter.limit("100/hour")
async def get_books(
    request: Request,
    category: Optional[str] =Query(None),
    min_price: Optional[float] =Query(None),
    max_price: Optional[float] = Query(None),
    rating: Optional[int] = Query(None),
    sort_by: Optional[str] =Query(None),
    page:int=  Query(1, ge=1), 
    limit: int=Query(20, ge=1, le=100)
    ):
    query = {}


    if category is not None:
        query["category"] = {"$regex": category.strip(), "$options": "i"}

  
    if min_price is not None or max_price is not None:
        expr = {"$toDouble": "$price_incl_tax"}
        conditions = []
        if min_price is not None:
            conditions.append({"$gte": [expr, min_price]})
        if max_price is not None:
            conditions.append({"$lte": [expr, max_price]})
        query["$expr"] = {"$and": conditions} if len(conditions) == 2 else conditions[0]

    if rating is not None:
        query["rating"] = rating

    skip = (page - 1) * limit

  
    pipeline = [{"$match": query}]

    if sort_by:
        if sort_by == "price":
            pipeline.append({"$addFields": {"price_num": {"$toDouble": "$price_incl_tax"}}})
            pipeline.append({"$sort": {"price_num": 1}})
        else:
            sort_field = "rating" if sort_by == "rating" else "num_reviews"
            pipeline.append({"$sort": {sort_field: 1}})

    pipeline.extend([
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {"_id": 0, "raw_html": 0, "content_hash": 0, "price_num": 0}}
    ])

    cursor = book_collection.aggregate(pipeline)
    result = await cursor.to_list(length=limit)
    return result


@app.get("/books/{book_id}")
@limiter.limit("100/hour")
async def get_book_by_id(book_id: str, request: Request):
    try:
        object_id = ObjectId(book_id)
    except Exception :
        raise HTTPException(status_code=400, detail="Invalid Id format")
    
    book = await book_collection.find_one({"_id": object_id})

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book["_id"] = str(book["_id"])
    return book


@app.get("/changes")
@limiter.limit("100/hour")
async def get_book_changes(request:Request):
    changes = await change_log_detection.find({}, {"_id": 0}).to_list(length=None)
    return changes