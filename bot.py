"""Grocery List Telegram Bot.

Shared grocery list for Dino and Katie.
Run with: python grocery/bot.py
"""

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Paths
PROJECT_ROOT = Path(__file__).parent
SECRETS_PATH = PROJECT_ROOT / "config" / "secrets.env"
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.json"

if SECRETS_PATH.exists():
    load_dotenv(SECRETS_PATH, override=True)

sys.path.insert(0, str(PROJECT_ROOT))

import db
import search as search_mod

logger = logging.getLogger(__name__)

# Pending clearall confirmations: user_id -> asyncio.Task
_clearall_pending: dict[int, asyncio.Task] = {}

CONFIRMATION_TIMEOUT = 30  # seconds


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return json.loads(SETTINGS_PATH.read_text())
    return {}


SETTINGS = load_settings()
ALLOWED_USERS: list[int] = SETTINGS.get("allowed_telegram_users", [])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_authorized(update: Update) -> bool:
    user_id = update.effective_user.id
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        logger.warning(f"Unauthorized access attempt from user_id={user_id} username={update.effective_user.username}")
        return False
    return True


def format_list(items: list[dict]) -> str:
    if not items:
        return "Your grocery list is empty."

    unchecked = [i for i in items if not i["checked"]]
    checked = [i for i in items if i["checked"]]

    lines = []

    if unchecked:
        lines.append("*Shopping list:*")
        for item in unchecked:
            qty = f" × {item['quantity']}" if item["quantity"] and item["quantity"] != "1" else ""
            notes = f" _{item['notes']}_" if item["notes"] else ""
            lines.append(f"  #{item['id']} {item['name']}{qty}{notes}")

    if checked:
        if unchecked:
            lines.append("")
        lines.append("*Checked off:*")
        for item in checked:
            qty = f" × {item['quantity']}" if item["quantity"] and item["quantity"] != "1" else ""
            lines.append(f"  ~~#{item['id']} {item['name']}{qty}~~")

    return "\n".join(lines)


def resolve_item(arg: str) -> tuple[dict | None, str]:
    """Resolve '#id' or 'name' to an item. Returns (item, error_message)."""
    arg = arg.strip()
    if arg.startswith("#"):
        try:
            item_id = int(arg[1:])
        except ValueError:
            return None, f"Invalid id: {arg}"
        item = db.get_by_id(item_id)
        if not item:
            return None, f"No item with id {arg}"
        return item, ""
    else:
        matches = db.find_by_name(arg)
        if not matches:
            return None, f"No item matching '{arg}'"
        if len(matches) == 1:
            return matches[0], ""
        # Multiple matches — return the first unchecked, else the first one
        unchecked = [m for m in matches if not m["checked"]]
        return (unchecked[0] if unchecked else matches[0]), ""


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text("Sorry, you're not authorized.")
        return
    await update.message.reply_text(
        "Grocery list bot.\n\n"
        "Commands:\n"
        "/add <item> [qty] — add item\n"
        "/remove <item or #id> — remove item\n"
        "/check <item or #id> — mark checked\n"
        "/uncheck <item or #id> — unmark\n"
        "/list — show full list\n"
        "/clear — remove all checked items\n"
        "/clearall — wipe entire list\n"
        "/search <query> — search for product info\n\n"
        "You can also just type an item name to quickly add it."
    )


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /add <item> [quantity]")
        return

    # Last arg is quantity if it looks like a number/amount, else default to '1'
    quantity = "1"
    if len(args) >= 2 and re.match(r"^[\d½¼¾]+[\w]*$", args[-1]):
        quantity = args[-1]
        name = " ".join(args[:-1])
    else:
        name = " ".join(args)

    added_by = str(update.effective_user.id)
    item_id = db.add_item(name=name, quantity=quantity, added_by=added_by)
    qty_str = f" × {quantity}" if quantity != "1" else ""
    await update.message.reply_text(f"Added: {name}{qty_str} (#{item_id})")


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /remove <item or #id>")
        return

    arg = " ".join(context.args)
    item, err = resolve_item(arg)
    if err:
        await update.message.reply_text(err)
        return

    db.remove_item(item["id"])
    await update.message.reply_text(f"Removed: {item['name']} (#{item['id']})")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /check <item or #id>")
        return

    arg = " ".join(context.args)
    item, err = resolve_item(arg)
    if err:
        await update.message.reply_text(err)
        return

    if item["checked"]:
        await update.message.reply_text(f"Already checked: {item['name']}")
        return

    db.set_checked(item["id"], True)
    await update.message.reply_text(f"Checked off: {item['name']} ✓")


async def uncheck_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /uncheck <item or #id>")
        return

    arg = " ".join(context.args)
    item, err = resolve_item(arg)
    if err:
        await update.message.reply_text(err)
        return

    if not item["checked"]:
        await update.message.reply_text(f"Not checked: {item['name']}")
        return

    db.set_checked(item["id"], False)
    await update.message.reply_text(f"Unchecked: {item['name']}")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    items = db.get_all_items()
    text = format_list(items)
    await update.message.reply_text(text, parse_mode="Markdown")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    count = db.clear_checked()
    if count == 0:
        await update.message.reply_text("No checked items to remove.")
    else:
        await update.message.reply_text(f"Removed {count} checked item(s).")


async def clearall_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return

    user_id = update.effective_user.id

    # If already pending confirmation, execute
    if user_id in _clearall_pending:
        _clearall_pending[user_id].cancel()
        del _clearall_pending[user_id]
        count = db.clear_all()
        await update.message.reply_text(f"List cleared. {count} item(s) removed.")
        return

    # First invocation — ask for confirmation
    await update.message.reply_text(
        f"This will delete everything. Send /clearall again within {CONFIRMATION_TIMEOUT}s to confirm."
    )

    async def expire_confirmation():
        try:
            await asyncio.sleep(CONFIRMATION_TIMEOUT)
        except asyncio.CancelledError:
            return
        finally:
            _clearall_pending.pop(user_id, None)

    _clearall_pending[user_id] = asyncio.create_task(expire_confirmation())


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /search <product query>")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"Searching for '{query}'...")

    # Run blocking playwright in executor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, search_mod.search_product, query)

    if not result["success"]:
        await update.message.reply_text(f"Search failed: {result['error']}")
        return

    content = result["content"]
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            await update.message.reply_text(content[i:i+4000])
    else:
        await update.message.reply_text(content)


# ---------------------------------------------------------------------------
# Free-text handler — quick add
# ---------------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text("Sorry, you're not authorized.")
        return

    text = update.message.text.strip()
    added_by = str(update.effective_user.id)

    # Check if the message looks like an existing item (fuzzy match)
    matches = db.find_by_name(text)
    unchecked_matches = [m for m in matches if not m["checked"]]

    if unchecked_matches and len(text) >= 3:
        item = unchecked_matches[0]
        db.set_checked(item["id"], True)
        await update.message.reply_text(f"Checked off: {item['name']} ✓\n(Send /uncheck #{item['id']} to undo)")
    else:
        # Add as new item
        item_id = db.add_item(name=text, quantity="1", added_by=added_by)
        await update.message.reply_text(f"Added: {text} (#{item_id})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)

    # Initialize database
    db.init_db()
    logger.info(f"Database ready at {db.DB_PATH}")

    if not ALLOWED_USERS:
        logger.warning("No allowed_telegram_users configured — bot is open to everyone!")
    else:
        logger.info(f"Allowed users: {ALLOWED_USERS}")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("uncheck", uncheck_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("clearall", clearall_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Grocery bot is running.")
    print("Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
