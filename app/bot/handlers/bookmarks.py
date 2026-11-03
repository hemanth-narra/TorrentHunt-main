from database import get_session
from database.models import Bookmark
from database.repositories import BookmarkRepository, TorrentCacheRepository
from localization import Translator
from structlog import get_logger
from telethon import events

from bot.decorators import setup_handler
from bot.handlers.inline import thumb
from bot.helpers import get_restricted_mode, is_explicit_hidden
from bot.views.bookmarks_view import render_bookmarks_menu
from bot.views.torrent_view import render_torrent

logger = get_logger(__name__)

BOOKMARK_THUMB = (
    "https://i.ibb.co/vYb4cY4/pngtree-bookmark-icon-vector-illustration-in-flat-style-"
    "for-any-purpose-png-image-975552.jpg"
)


def row2dict(row: Bookmark) -> dict[str, str]:
    return {
        column.name: str(getattr(row, column.name))
        for column in row.__table__.columns
    }


def parse_torrent_message(text: str) -> dict[str, str]:
    """Recover the torrent fields from a magnet message's plain text fallback."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return {}

    title = lines[0][2:] if len(lines[0]) > 2 else lines[0]
    size = ""
    seeders = "0"
    leechers = "0"
    uploaded_on = ""
    magnet = ""

    for line in lines[1:]:
        if line.startswith("magnet:?"):
            magnet = line
        elif ":" in line:
            val = line.split(":", 1)[1].strip()
            if not size:
                size = val
            elif seeders == "0":
                seeders = val
            elif leechers == "0":
                leechers = val
            elif not uploaded_on:
                uploaded_on = val

    return {
        "title": title,
        "size": size,
        "seeders": seeders,
        "leechers": leechers,
        "uploaded_on": uploaded_on,
        "magnet": magnet,
    }


@setup_handler()
async def bookmarks_menu(event: events.NewMessage.Event, t: Translator) -> None:
    view = render_bookmarks_menu(t)
    await event.respond(view.message, buttons=view.buttons, reply_to=event.id)


@setup_handler()
async def add_bookmark(event: events.CallbackQuery.Event, t: Translator) -> None:
    info_hash = event.data.decode().split("_")[1]

    async with get_session() as session:
        bookmarks = BookmarkRepository(session)

        if not await bookmarks.exists(event.sender_id, info_hash):
            cache_row = await TorrentCacheRepository(session).get_by_hash(info_hash)
            if cache_row:
                await bookmarks.add(
                    event.sender_id,
                    info_hash,
                    title=cache_row.name,
                    magnet=cache_row.magnet,
                    seeders=str(cache_row.seeders),
                    leechers=str(cache_row.leechers),
                    size=cache_row.size or "",
                    uploaded_on=cache_row.uploaded_on or "",
                )
            else:
                message = await event.get_message()
                fields = parse_torrent_message(message.raw_text or "")
                if fields:
                    await bookmarks.add(event.sender_id, info_hash, **fields)

    await event.answer(t.get("wishlistAdded"))


@setup_handler()
async def remove_bookmark(event: events.CallbackQuery.Event, t: Translator) -> None:
    info_hash = event.data.decode().split("_")[1]

    async with get_session() as session:
        await BookmarkRepository(session).remove(event.sender_id, info_hash)

    await event.answer(t.get("wishlistRemoved"))


@setup_handler()
async def bookmarks_inline(event: events.InlineQuery.Event, t: Translator) -> None:
    restricted_mode = await get_restricted_mode(event.sender_id)
    results = []

    offset = int(event.offset) if event.offset else 0

    async with get_session() as session:
        rows = await BookmarkRepository(session).list_page(event.sender_id, offset)

    next_offset = None

    if rows:
        for row in rows:
            data = row2dict(row)
            view = render_torrent(
                data,
                t,
                explicit_hidden=is_explicit_hidden(data, restricted_mode),
                bookmarked=True,
            )
            results.append(
                event.builder.article(
                    title=data.get("title", ""),
                    description=view.description,
                    text=view.message,
                    buttons=view.buttons,
                    thumb=thumb(BOOKMARK_THUMB),
                    link_preview=False,
                ),
            )

        if len(rows) == 50:
            next_offset = offset + 1

    await event.answer(
        results,
        cache_time=10,
        next_offset=str(next_offset) if next_offset else None,
        switch_pm=t.get("bookmarks"),
        switch_pm_param="bookmarks",
    )
