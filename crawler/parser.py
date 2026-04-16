import json
import hashlib
from bs4 import BeautifulSoup
import httpx
import asyncio
from decimal import Decimal  
from urllib.parse import urljoin
from utilities.database import book_collection, change_log_detection, run_setup
from datetime import datetime, UTC
from models.book import Book 


full_URL = 'https://books.toscrape.com/'

async def scrape_book_details(client, book_url, limitation): 
    async with limitation:
        response = await client.get(book_url)

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1').text
    description_raw = soup.find('article',class_='product_page').find_all('p')[3].text
    category_raw = soup.find('ul',class_='breadcrumb').find_all('li')[2].text
    price_incl_tax_raw = soup.find('table',class_='table table-striped').find_all('tr')[3].find('td').text
    price_excl_tax_raw = soup.find('table',class_='table table-striped').find_all('tr')[2].find('td').text
    availability_raw = soup.find('table',class_='table table-striped').find_all('tr')[5].find('td').text
    num_reviews_raw = soup.find('table',class_='table table-striped').find_all('tr')[6].find('td').text
    image_url_book_cover_raw = soup.find('div',class_=['item','active']).find('img').get('src')
    rating_raw = soup.find('p', class_='star-rating')

    num_reviews_final = int("".join(char for char in num_reviews_raw if char.isdigit()))

    clean_image_url = full_URL + image_url_book_cover_raw.replace('../', '')

    #Checks weather the price has a currency symbol and then removes it and then converts it to decimal 
    price_incl_tax_final = Decimal("".join(char for char in price_incl_tax_raw if char.isdigit() or char == '.'))
    price_excl_tax_final = Decimal("".join(char for char in price_excl_tax_raw if char.isdigit() or char == '.'))

    #checking if there is stock in boolean
    if "in stock" in availability_raw.lower():
        is_available = True
    else:
        is_available = False


   #getting the word number amount of the book rating  
    classes = rating_raw.get('class')
    rating_word = classes[1]
    
    rating_map ={
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    rating_number = rating_map.get(rating_word, 0)

    return {
        "name": title,
        "description": description_raw,
        "category": category_raw,
        "price_incl_tax": price_incl_tax_final,
        "price_excl_tax": price_excl_tax_final,
        "availability": is_available,
        "num_reviews": num_reviews_final,
        "rating": rating_number,
        "image_url": clean_image_url
    }

 
async def generate_content_hash(book_data: dict) -> str: 
        relevant_data = {
            "name": book_data.get("name"),
            "price_incl_tax": str(book_data.get("price_incl_tax")),
            "availability": book_data.get("availability"),
            "rating": book_data.get("rating")
        }

        data_string = json.dumps(relevant_data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(data_string).hexdigest()


async def main(): 
    await run_setup()
    all_book_data = []
    current_url = full_URL
    limitation = asyncio.Semaphore(5)
    
    async with httpx.AsyncClient() as client: 
        while current_url:
            response = await client.get(current_url)
            soup = BeautifulSoup(response.text, "html.parser")
            #Raw metadata  
            raw_html = response.text
            page_tasks = []
            book_urls = []

            for container in soup.find_all('div',class_='image_container'):
                anchor_tag = container.find('a')
                if anchor_tag:
                    href = anchor_tag.get('href')
                    book_url = urljoin(current_url, href)
                    book_urls.append(book_url)
                    page_tasks.append(scrape_book_details(client, book_url, limitation))
            print(f"Batch Scrape {len(page_tasks)} books...")
            results = await asyncio.gather(*page_tasks)
            
            new_books = []
            content_check =  ["name", "availability", "rating", "price_incl_tax"]
           

            for book_data, source_url in zip(results, book_urls):
                 existing_book = await book_collection.find_one({"source_url":source_url})
                 current_content_hash = await generate_content_hash(book_data)

                 if book_data: 
                    book_data['source_url'] = source_url
                    book_data['raw_html'] = raw_html
                    book_data['status'] = "scraped"
                    book_data['crawl_timestamp'] = datetime.now(UTC)
                    book_data['content_hash'] = current_content_hash
                    
                    book_model = Book(**book_data)
                    book_document = book_model.model_dump(mode="json")
                    

                 if existing_book:

                    if existing_book["content_hash"] != current_content_hash:
                        print(f"Changes found in {source_url}")
                        changed_values = {}
                        
                        for field in content_check:
                            if book_data[field] != existing_book.get(field):
                                changed_values[field] = {
                                    "old_value :" : existing_book.get(field),
                                    "new_value :" : book_document[field]}
                                
                        if changed_values: 
                            change_log = {
                                "source_url": source_url,
                                "timestamp" : datetime.now(UTC),
                                "changes": changed_values
                            }
                            await change_log_detection.insert_one(change_log)
                        await book_collection.replace_one({"source_url": source_url}, book_document)    
                    else:
                        print("No changes found")
                 else:
                     new_books.append(book_document)
                
                 
                 

            if new_books:
                try:
                    await book_collection.insert_many(new_books)
                    all_book_data.extend(new_books)
                    print(f"Successfully saved batch: Total saved{len(all_book_data)}")
                except Exception as e:
                    print(f"Database error {e}")
       
            next_tag = soup.find('li',class_= 'next')
            if next_tag: 
                next_ref = next_tag.find('a').get('href')
                current_url = urljoin(current_url, next_ref)
            else: 
                print("No more pages to scrape.")
                current_url = None
    return all_book_data
      
        


asyncio.run(main())