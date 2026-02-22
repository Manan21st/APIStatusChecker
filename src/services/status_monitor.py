import os
import re
import html
from typing import Dict, List

import httpx
import feedparser

class StatusMonitorService:
    def __init__(self, feed_url: str = None):
        self.feed_url = feed_url or os.getenv("STATUS_FEED_URL", "https://status.openai.com/feed.atom")
        self.etag = None
        self.client = httpx.AsyncClient(timeout=10.0)
        self.recent_incidents: List[Dict] = []
        self.max_incidents: int = 20

    def _strip_html(self, text: str) -> str:
        """
        Remove HTML tags and decode HTML entities while preserving spacing.
        """
        if not text:
            return ""
        text = html.unescape(text)
        text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>|<p>', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'</li>|<li>', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def check_feed(self):
        headers = {}
        if self.etag:
            headers["If-None-Match"] = self.etag

        response = await self.client.get(self.feed_url, headers=headers)

        if response.status_code == 304:
            return

        if response.status_code == 200:
            self.etag = response.headers.get("ETag")
            feed = feedparser.parse(response.text)

            for entry in feed.entries[:1]:
                incident = {
                    "id": getattr(entry, "id", None) or getattr(entry, "link", None) or entry.title,
                    "title": entry.title,
                    "summary": self._strip_html(entry.summary),
                    "updated": entry.updated,
                }
                self._add_incident(incident)

                print(f"[{entry.updated}] Product: {entry.title}")
                print(f"{incident['summary']}")

    def _add_incident(self, incident: Dict) -> None:
        incident_id = incident.get("id")
        if incident_id:
            existing_ids = [inc.get("id") for inc in self.recent_incidents]
            if incident_id in existing_ids:
                return 
        
        self.recent_incidents.append(incident)
        if len(self.recent_incidents) > self.max_incidents:
            self.recent_incidents = self.recent_incidents[-self.max_incidents :]