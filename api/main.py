from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from utilities.database import book_collection, change_log_detection
from bson import ObjectId
app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


from fastapi import Query
from typing import Optional

@app.get("/books")
async def get_books(
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
async def get_book_by_id(book_id: str):
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
async def get_book_changes():
    changes = await change_log_detection.find({}, {"_id": 0}).to_list(length=None)
    return changes