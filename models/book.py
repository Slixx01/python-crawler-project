from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal 
class Book(BaseModel):
    name: str
    description : (Optional[str]) 
    category : str
    image_url : str
    price_incl_tax : Decimal
    price_excl_tax : Decimal
    availability : bool
    num_reviews : int
    rating : int
    crawl_timestamp : datetime 
    source_url: str 
    content_hash : str
    raw_html: str
    status: str
