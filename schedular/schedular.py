import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawler.parser import main 

async def run():
    schedular = AsyncIOScheduler()
    job_id = schedular.add_job(main, 'interval', seconds=10)
    schedular.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        schedular.shutdown()
asyncio.run(run())