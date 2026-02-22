from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/incidents", tags=["Status"])
async def get_recent_incidents(request: Request):
    """
    Return recent incidents detected from the status feed.
    """
    app = request.app
    monitor_service = getattr(app.state, "monitor_service", None)
    poll_interval = getattr(app.state, "poll_interval", None)

    if monitor_service is None:
        return {"feed_url": None, "poll_interval": poll_interval, "count": 0, "incidents": []}

    incidents = monitor_service.recent_incidents

    return {
        "feed_url": monitor_service.feed_url,
        "poll_interval": poll_interval,
        "count": len(incidents),
        "incidents": incidents,
    }