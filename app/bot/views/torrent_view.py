"""View for a single torrent: the magnet message and its buttons."""

from html import escape
from typing import Any

from config import settings
from localization import Translator
from telethon import Button

from bot.views import ViewResponse

content_template = """{magnet_icon} <b>{title}</b>
<blockquote>{size_str}: {size}
{seeders_str}: {seeders}
{leechers_str}: {leechers}
{uploaded_on_str}: {uploaded_on}</blockquote>

<b>{magnet_link_str} (Tap to Copy):</b>
<code>{magnet}</code>
"""


def render_torrent(
    data: dict[str, Any],
    t: Translator,
    explicit_hidden: bool = False,
    bookmarked: bool = False,
) -> ViewResponse:
    title = data.get("name") or data.get("title")

    # Unresolvable torrent (expired id, bad data)
    if not title:
        return ViewResponse(message=t.get("errorFetchingLink"))

    # Summary line for inline results
    description = "{} {}, {} {}, {} {}, {} {}".format(
        t.get("storageIcon"),
        data.get("size"),
        t.get("seedersIcon"),
        data.get("seeders"),
        t.get("leechersIcon"),
        data.get("leechers"),
        t.get("dateIcon"),
        data.get("uploaded_on"),
    )

    # Hidden by restricted mode
    if explicit_hidden:
        return ViewResponse(message=t.get("cantView"), description=description)

    magnet_link = data.get("magnet_link") or data.get("magnetLink") or data.get("magnet") or ""

    message = content_template.format(
        magnet_icon=t.get("magnetIcon"),
        title=escape(title),
        size=data.get("size") or "—",
        seeders=data.get("seeders") or 0,
        leechers=data.get("leechers") or 0,
        uploaded_on=data.get("date_uploaded") or data.get("uploadDate") or data.get("uploaded_on") or "—",
        magnet=escape(magnet_link),
        size_str=t.get("size"),
        seeders_str=t.get("seeders"),
        leechers_str=t.get("leechers"),
        uploaded_on_str=t.get("uploadedOn"),
        magnet_link_str=t.get("link"),
    )

    info_hash = data.get("info_hash") or data.get("infoHash") or data.get("hash") or ""
    seedr_bot = (settings.seedr_bot_username or "hemanthseedrobot").lstrip("@")

    if bookmarked:
        bookmark_button = Button.inline(
            t.get("removeFromBookmarkBtn"),
            f"removeFromBookmark_{info_hash}".encode(),
        )
    else:
        bookmark_button = Button.inline(
            t.get("addToBookmarkBtn"),
            f"addToBookmark_{info_hash}".encode(),
        )

    buttons = [
        [
            Button.url(
                f"🌱 Send to @{seedr_bot}",
                f"https://t.me/{seedr_bot}?start=addTorrent_{info_hash}",
            ),
        ],
        [bookmark_button],
    ]

    return ViewResponse(message=message, buttons=buttons, description=description)
