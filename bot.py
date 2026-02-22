"""Grocery List Discord Bot.

Shared grocery list for Dino and Katie.
Slash commands + free-text quick-add in the configured grocery channel.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

import discord
from discord import app_commands
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
SECRETS_PATH = PROJECT_ROOT / "config" / "secrets.env"
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.json"

if SECRETS_PATH.exists():
    load_dotenv(SECRETS_PATH, override=True)

sys.path.insert(0, str(PROJECT_ROOT))
import db
import search as search_mod

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return json.loads(SETTINGS_PATH.read_text())
    return {}

SETTINGS = load_settings()
ALLOWED_USERS: list[int] = SETTINGS.get("allowed_discord_users", [])
GROCERY_CHANNEL_ID: int | None = SETTINGS.get("grocery_channel_id")


# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True

class GroceryBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Slash commands synced")

bot = GroceryBot()
tree = bot.tree


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def is_authorized(interaction: discord.Interaction) -> bool:
    if ALLOWED_USERS and interaction.user.id not in ALLOWED_USERS:
        logger.warning(f"Unauthorized: {interaction.user} ({interaction.user.id})")
        return False
    return True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_list(items: list[dict]) -> str:
    if not items:
        return "Grocery list is empty."

    unchecked = [i for i in items if not i["checked"]]
    checked   = [i for i in items if i["checked"]]
    lines = []

    if unchecked:
        lines.append("**Shopping list:**")
        for item in unchecked:
            qty   = f" × {item['quantity']}" if item["quantity"] and item["quantity"] != "1" else ""
            notes = f" *{item['notes']}*" if item["notes"] else ""
            lines.append(f"  `#{item['id']}` {item['name']}{qty}{notes}")

    if checked:
        if unchecked:
            lines.append("")
        lines.append("**Checked off:**")
        for item in checked:
            qty = f" × {item['quantity']}" if item["quantity"] and item["quantity"] != "1" else ""
            lines.append(f"  ~~`#{item['id']}` {item['name']}{qty}~~")

    return "\n".join(lines)


def resolve_item(arg: str) -> tuple[dict | None, str]:
    arg = arg.strip()
    if arg.startswith("#"):
        try:
            item_id = int(arg[1:])
        except ValueError:
            return None, f"Invalid id: `{arg}`"
        item = db.get_by_id(item_id)
        return (item, "") if item else (None, f"No item with id `{arg}`")
    else:
        matches = db.find_by_name(arg)
        if not matches:
            return None, f"No item matching `{arg}`"
        unchecked = [m for m in matches if not m["checked"]]
        return (unchecked[0] if unchecked else matches[0]), ""


async def grocery_channel() -> discord.TextChannel | None:
    if not GROCERY_CHANNEL_ID:
        return None
    ch = bot.get_channel(GROCERY_CHANNEL_ID)
    if ch is None:
        ch = await bot.fetch_channel(GROCERY_CHANNEL_ID)
    return ch


async def notify_other(actor: discord.User | discord.Member, message: str):
    """Post a notification to the grocery channel (visible to everyone)."""
    ch = await grocery_channel()
    if ch:
        await ch.send(message)


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------

@tree.command(name="add", description="Add an item to the grocery list")
@app_commands.describe(item="Item name", quantity="Quantity (default: 1)")
async def add_cmd(interaction: discord.Interaction, item: str, quantity: str = "1"):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    item_id = db.add_item(name=item, quantity=quantity, added_by=str(interaction.user.id))
    qty_str = f" × {quantity}" if quantity != "1" else ""
    reply = f"Added: **{item}**{qty_str} (`#{item_id}`)"
    await interaction.response.send_message(reply)
    # Notify if sent outside grocery channel
    ch = await grocery_channel()
    if ch and interaction.channel_id != GROCERY_CHANNEL_ID:
        await ch.send(f"🛒 {interaction.user.display_name} added **{item}**{qty_str}")


@tree.command(name="remove", description="Remove an item from the list")
@app_commands.describe(item="Item name or #id")
async def remove_cmd(interaction: discord.Interaction, item: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    row, err = resolve_item(item)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    db.remove_item(row["id"])
    await interaction.response.send_message(f"Removed: **{row['name']}** (`#{row['id']}`)")


@tree.command(name="check", description="Mark an item as checked off")
@app_commands.describe(item="Item name or #id")
async def check_cmd(interaction: discord.Interaction, item: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    row, err = resolve_item(item)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    if row["checked"]:
        await interaction.response.send_message(f"Already checked: **{row['name']}**", ephemeral=True)
        return
    db.set_checked(row["id"], True)
    await interaction.response.send_message(f"Checked off: **{row['name']}** ✓")


@tree.command(name="uncheck", description="Uncheck an item")
@app_commands.describe(item="Item name or #id")
async def uncheck_cmd(interaction: discord.Interaction, item: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    row, err = resolve_item(item)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    if not row["checked"]:
        await interaction.response.send_message(f"Not checked: **{row['name']}**", ephemeral=True)
        return
    db.set_checked(row["id"], False)
    await interaction.response.send_message(f"Unchecked: **{row['name']}**")


@tree.command(name="list", description="Show the grocery list")
async def list_cmd(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    items = db.get_all_items()
    await interaction.response.send_message(format_list(items))


@tree.command(name="clear", description="Remove all checked items")
async def clear_cmd(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    count = db.clear_checked()
    if count == 0:
        await interaction.response.send_message("No checked items to remove.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Removed {count} checked item(s).")


# Clearall confirmation tracking: user_id -> asyncio.Task
_clearall_pending: dict[int, asyncio.Task] = {}
CONFIRMATION_TIMEOUT = 30

@tree.command(name="clearall", description="Wipe the entire list (requires confirmation)")
async def clearall_cmd(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return

    user_id = interaction.user.id

    if user_id in _clearall_pending:
        _clearall_pending[user_id].cancel()
        del _clearall_pending[user_id]
        count = db.clear_all()
        await interaction.response.send_message(f"List cleared. {count} item(s) removed.")
        return

    await interaction.response.send_message(
        f"This will delete everything. Run `/clearall` again within {CONFIRMATION_TIMEOUT}s to confirm.",
        ephemeral=True
    )

    async def expire():
        try:
            await asyncio.sleep(CONFIRMATION_TIMEOUT)
        except asyncio.CancelledError:
            return
        finally:
            _clearall_pending.pop(user_id, None)

    _clearall_pending[user_id] = asyncio.create_task(expire())


@tree.command(name="search", description="Search for product info")
@app_commands.describe(query="Product to search for")
async def search_cmd(interaction: discord.Interaction, query: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return

    await interaction.response.defer()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, search_mod.search_product, query)

    if not result["success"]:
        await interaction.followup.send(f"Search failed: {result['error']}")
        return

    content = result["content"]
    # Discord message limit 2000 chars — chunk if needed
    chunks = [content[i:i+1900] for i in range(0, min(len(content), 4000), 1900)]
    for chunk in chunks:
        await interaction.followup.send(f"```\n{chunk}\n```")


# ---------------------------------------------------------------------------
# Free-text handler — quick add/check in grocery channel
# ---------------------------------------------------------------------------

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if GROCERY_CHANNEL_ID and message.channel.id != GROCERY_CHANNEL_ID:
        return
    if message.content.startswith("/"):
        return  # Let slash commands handle it

    if ALLOWED_USERS and message.author.id not in ALLOWED_USERS:
        return

    text = message.content.strip()
    if not text:
        return

    matches = db.find_by_name(text)
    unchecked = [m for m in matches if not m["checked"]]

    if unchecked and len(text) >= 3:
        item = unchecked[0]
        db.set_checked(item["id"], True)
        await message.reply(f"Checked off: **{item['name']}** ✓  (use `/uncheck #{item['id']}` to undo)")
    else:
        item_id = db.add_item(name=text, quantity="1", added_by=str(message.author.id))
        await message.reply(f"Added: **{text}** (`#{item_id}`)")


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    logger.info(f"Grocery bot ready: {bot.user} ({bot.user.id})")
    if GROCERY_CHANNEL_ID:
        logger.info(f"Grocery channel: {GROCERY_CHANNEL_ID}")
    else:
        logger.warning("No grocery_channel_id configured — free-text add disabled")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )

    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN not set in config/secrets.env")
        sys.exit(1)

    db.init_db()
    logger.info(f"DB ready at {db.DB_PATH}")

    if not ALLOWED_USERS:
        logger.warning("No allowed_discord_users — bot open to everyone in the channel")

    bot.run(token)


if __name__ == "__main__":
    main()
