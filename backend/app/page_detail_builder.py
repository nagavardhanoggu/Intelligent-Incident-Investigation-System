from copy import deepcopy
import re
from typing import Any


def build_subpage_payload(parent_payload: dict[str, Any], subpage_key: str) -> dict[str, Any]:
    explicit_subpages = parent_payload.get("subpages") or {}
    explicit = explicit_subpages.get(subpage_key)
    if explicit:
        return deepcopy(explicit)

    for section in parent_payload.get("sections") or []:
        for item in section.get("items") or []:
            item_key = str(item.get("detailKey") or slugify(str(item.get("title", ""))))
            if item_key == subpage_key:
                return _item_detail_payload(parent_payload, section, item)

    raise KeyError(subpage_key)


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "detail"


def _item_detail_payload(parent_payload: dict[str, Any], section: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    tags = [str(tag) for tag in item.get("tags") or []]
    status = str(item.get("status") or "Tracked")
    parent_title = str(parent_payload.get("title") or "Page")
    section_title = str(section.get("title") or "Records")
    parent_pill = parent_payload.get("pill") or {}
    progress = item.get("progress")

    kpis = [
        {
            "label": "Source Page",
            "value": parent_title,
            "helper": section_title,
            "icon": parent_pill.get("icon") or "dashboard",
            "state": "healthy",
        },
        {
            "label": "Status",
            "value": status,
            "helper": item.get("meta") or item.get("subtitle") or "Stored page record",
            "icon": item.get("icon") or "flag",
            "state": _status_state(status),
        },
        {
            "label": "Tags",
            "value": str(len(tags)),
            "helper": ", ".join(tags) if tags else "No tags stored",
            "icon": "sell",
            "state": "healthy",
        },
    ]

    if progress is not None:
        kpis.append(
            {
                "label": "Progress",
                "value": f"{progress}%",
                "helper": "Stored progress indicator",
                "icon": "trending_up",
                "state": _progress_state(progress),
            }
        )

    overview_items = [
        {
            "title": item.get("title") or parent_title,
            "subtitle": item.get("subtitle") or section.get("caption"),
            "detail": item.get("detail") or parent_payload.get("subtitle") or "",
            "meta": item.get("meta"),
            "status": status,
            "icon": item.get("icon") or parent_pill.get("icon") or "article",
            "progress": progress,
            "tags": tags,
            "route": item.get("route"),
        }
    ]

    related_items = []
    for related in section.get("items") or []:
        if related is item:
            continue
        related_item = deepcopy(related)
        related_item.setdefault("detailKey", slugify(str(related_item.get("title", ""))))
        related_items.append(related_item)
        if len(related_items) == 4:
            break

    sections = [
        {
            "title": "Record Overview",
            "caption": item.get("subtitle") or section.get("caption") or section_title,
            "items": overview_items,
        }
    ]
    if related_items:
        sections.append(
            {
                "title": "Related Records",
                "caption": section_title,
                "items": related_items,
            }
        )

    return {
        "title": item.get("title") or parent_title,
        "subtitle": item.get("detail") or parent_payload.get("subtitle") or "",
        "pill": {
            "icon": item.get("icon") or parent_pill.get("icon") or "article",
            "label": status,
        },
        "kpis": kpis,
        "sections": sections,
        "parentTitle": parent_title,
    }


def _status_state(status: str) -> str:
    normalized = status.lower()
    if any(term in normalized for term in ["critical", "blocked", "breach", "failed"]):
        return "critical"
    if any(term in normalized for term in ["open", "pending", "review", "watch", "warning", "risk", "draft", "planned"]):
        return "warning"
    return "healthy"


def _progress_state(progress: Any) -> str:
    try:
        value = float(progress)
    except (TypeError, ValueError):
        return "healthy"
    if value < 50:
        return "warning"
    return "healthy"
