# python-crawler-project

This project is about a crawler and scraper scraping books.toscrape.com to gather data on the books. This program is written with python 12.7 and the data is stored in a MongoDB and then the API is used to quary the database and  get the results of the API endpoints 

The folder structre looks as follows 

python-crawler-project/
├── api/
│   └── main.py              - FastAPI application and endpoints
├── crawler/
│   └── parser.py            - Async web crawler
├── scheduler/
│   └── scheduler.py         - APScheduler + daily CSV report
├── models/
│   └── book.py              - Pydantic Book schema
├── utilities/
│   ├── database.py          - MongoDB connection
│   └── logger.py            - Logging setup
├── tests/
│   └── test_api.py          - API tests
├── logs/                    - Auto-generated log files
├── reports/                 - Auto-generated daily CSV reports
├── conftest.py              - Pytest configuration
├── pytest.ini               - Pytest settings
├── .env                     - Environment variables (not committed)
├── .env.example             - Example environment variables
├── .gitignore
├── requirements.txt
└── README.md

There are 3 API endpoints books books with a id and then the changes endpoint 
The first api will gather the books related to the searching results that will be implemented 
The second api endpoint will gather the book details of a single book of of the id that mongoDB generates for each record in the database 
The thirs api endpoint will get the changes that has been made in the database before and will show the result of what has been changes 

Setup

1. Clone the repo and create a virtual environment
2. Run `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your values

Running the project

- Crawler: `python crawler/parser.py`
- Scheduler: `python scheduler/scheduler.py`  
- API: `uvicorn api.main:app --reload` then go to `http://localhost:8000`

Environment variables

MONGO_URI=mongodb://localhost:27017
API_KEY=your_key_here  

Generate a key by running: `python -c "import secrets; print(secrets.token_hex(32))"`

Tests

pytest tests/test_api.py -v