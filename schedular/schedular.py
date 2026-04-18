import asyncio
import os 
import csv
from datetime import datetime, timedelta, UTC
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from crawler.parser import main 
from utilities.logger import get_logger
from utilities.database import change_log_detection

logger = get_logger("schedular")

async def generate_daily_report():
    os.makedirs("reports", exist_ok=True)

    today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)    
    tomorrow = today + timedelta(days=1)

    changes = await change_log_detection.find({
        {"timestaps": {"$gte":today, "$lte": tomorrow}},
        {"_id": 0}
    }).to_list(length=None)

    if not changes:
        logger.info("No changes today, skipping report")
        return
    
    filename = f"reports/change_report_{today.strftime('%Y-%m-%d')}.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source_url", "timestamp", "field", "old_value", "new_value"])

        for change in changes:
            for field, values in change.get("changes", {}).items():
                 writer.writerow([
                    change["source_url"],
                    change["timestamp"],
                    field,
                    values["old_value"],
                    values["new_value"]
                ])
    logger.info(f"Daily report saved to {filename}")

async def run():
    schedular = AsyncIOScheduler()
    schedular.add_job(main, 'interval', hours=24)
    schedular.add_job(generate_daily_report, 'cron', hour=23, minute=59)
    schedular.start()
    logger.info("Schedular started...")
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        schedular.shutdown()
asyncio.run(run())
