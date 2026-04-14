from bs4 import BeautifulSoup
import httpx
import asyncio
from decimal import Decimal  
from urllib.parse import urljoin 
full_URL = 'https://books.toscrape.com/'

async def scrape_book_details(client, book_url): 

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
        "title": title,
        "description": description_raw,
        "category": category_raw,
        "price_incl": price_incl_tax_final,
        "price_excl": price_excl_tax_final,
        "available": is_available,
        "reviews": num_reviews_final,
        "rating": rating_number,
        "image": clean_image_url
    }


async def main(): 

    all_book_data = []

    async with httpx.AsyncClient() as client: 
        response = await client.get(full_URL)
        soup = BeautifulSoup(response.text, "html.parser")
    
        for container in soup.find_all('div',class_='image_container'):
            anchor_tag = container.find('a')

            if anchor_tag:
                href = anchor_tag.get('href')
                book_url = urljoin(full_URL, href)
                print(f"Scrapping: {book_url}")
                book_details = await scrape_book_details(client, book_url)
                all_book_data.append(book_details)
    print(f"successfully scraped {len(all_book_data)} books.")

    return all_book_data
      
        


asyncio.run(main())