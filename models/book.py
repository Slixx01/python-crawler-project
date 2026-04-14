from pydantic import BaseModel
from datetime import datetime 
class Book(BaseModel):
    Name: str
    Description : str 
    Category : str
    ImageURL : str
    PriceTax : float
    PriceNotTax : float
    Availability : bool
    Numreviews : int
    Rating : int
    CrawlTimeStamp : datetime 
    SourceURL: str 
    ContentHash : str

