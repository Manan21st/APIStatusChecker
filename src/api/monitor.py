import os
import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from services.status_monitor import StatusMonitorService

load_dotenv()

logger = logging.getLogger(__name__)


async def _run_polling_loop(monitor_service: StatusMonitorService, interval: int = 60):
    """
    Background loop that polls the feed at the specified interval.
    """
    while True:
        try:
            await monitor_service.check_feed()
        except Exception as e:
            logger.exception("Error during status feed check: %s", e)
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app):
    """
    Start background status monitor on startup; cancel on shutdown.
    """
    feed_url = os.getenv("STATUS_FEED_URL")
    poll_interval = int(os.getenv("POLL_INTERVAL", "60"))

    monitor_service = StatusMonitorService(feed_url=feed_url)
    app.state.monitor_service = monitor_service
    app.state.poll_interval = poll_interval

    task = asyncio.create_task(_run_polling_loop(monitor_service, poll_interval))

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    try:
        await monitor_service.client.aclose()
    except Exception as e:
        logger.exception("Error closing client: %s", e)
