import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawler.parser import main 
from utilities.logger import get_logger

logger = get_logger("schedular")

async def run():
    schedular = AsyncIOScheduler()
    job_id = schedular.add_job(main, 'interval', seconds=10)
    schedular.start()
    logger.info("Schedular started...")
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        schedular.shutdown()
asyncio.run(run())