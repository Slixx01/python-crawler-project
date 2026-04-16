from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawler.parser import main 


schedular = AsyncIOScheduler()
job_id = schedular.add_job(main, 'interval', minutes=1)


schedular.start()