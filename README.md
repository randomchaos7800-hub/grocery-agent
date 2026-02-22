# Grocery Agent

Shared grocery list for Dino and Katie. Discord bot with slash commands, free-text quick-add, and Playwright product search.

**Status: Active — Discord migration complete. Expanding.**

---

## What It Does

- Shared grocery list via Discord
- Slash commands: `/add`, `/remove`, `/check`, `/uncheck`, `/list`, `/clear`, `/clearall`, `/search`
- Free-text in `#grocery` channel: type an item → added. Type a name matching something on the list → checked off.
- `/search <query>` — headless Playwright search via DuckDuckGo for product info
- SQLite persistence (`grocery.db`)
- `/clearall` with 30s confirmation window

---

## Commands

| Command | Description |
|---------|-------------|
| `/add <item> [quantity]` | Add item to list |
| `/remove <item or #id>` | Remove item |
| `/check <item or #id>` | Mark checked off |
| `/uncheck <item or #id>` | Unmark |
| `/list` | Show full list |
| `/clear` | Remove all checked items |
| `/clearall` | Wipe entire list (requires re-run to confirm) |
| `/search <query>` | Search for product info |
| `<text>` in #grocery | Quick-add, or check off if name matches |

Items referenced by name (`milk`) or ID (`#12`). Partial name matching works.

---

## Planned Expansions

- [ ] LLM-assisted search — actual product info, prices, substitutions
- [ ] Smart add — "we need breakfast stuff" → suggests items based on history
- [ ] Recurring items — staples that auto-reappear when cleared
- [ ] Categories / aisle grouping
- [ ] Cross-user notifications (Katie adds → Dino gets pinged)
- [ ] Store price comparison
- [ ] FinEngine integration — grocery spend tracked against weekly $150 budget
- [ ] Kato awareness — Kato can read/update the list on Dino's behalf

---

## Architecture

```
bot.py      — Discord bot, slash commands, free-text handler
db.py       — SQLite layer (items: id, name, qty, category, checked, added_by, notes)
search.py   — Playwright headless search via DuckDuckGo
grocery.db  — SQLite database (not committed)
grocery.service — systemd unit file
```

**Runtime:** Python 3.10+, venv
**Interface:** Discord (discord.py v2.4)
**DB:** SQLite at `grocery/grocery.db`
**Search:** Playwright + Chromium headless

---

## Setup

```bash
cd grocery
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp config/secrets.env.example config/secrets.env
# edit: add DISCORD_BOT_TOKEN

cp config/settings.json.example config/settings.json
# edit: add allowed_discord_users IDs, set grocery_channel_id
```

### Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Create a new application → Bot → copy token → add to `config/secrets.env`
3. Enable **Message Content Intent** under Bot → Privileged Gateway Intents
4. Invite URL: `https://discord.com/oauth2/authorize?client_id=<APP_ID>&scope=bot+applications.commands&permissions=2048`
5. Create a `#grocery` channel in your server, copy its ID → add to `settings.json` as `grocery_channel_id`
6. Add your Discord user ID to `allowed_discord_users`

### Run

```bash
python bot.py
```

### systemd (production)

```bash
sudo cp grocery.service /etc/systemd/system/
sudo systemctl enable grocery
sudo systemctl start grocery
```

---

## Config

### `config/secrets.env`
```
DISCORD_BOT_TOKEN=your_token_here
```

### `config/settings.json`
```json
{
  "allowed_discord_users": [your_discord_user_id],
  "grocery_channel_id": your_grocery_channel_id,
  "search": { "timeout_ms": 15000 }
}
```

Get your Discord user ID: Discord → Settings → Advanced → enable Developer Mode → right-click your username → Copy User ID.

---

## Database Schema

```sql
CREATE TABLE items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    quantity    TEXT DEFAULT '1',
    category    TEXT DEFAULT '',
    checked     INTEGER DEFAULT 0,
    added_by    TEXT NOT NULL,
    added_at    TEXT NOT NULL,
    notes       TEXT DEFAULT ''
);
```

---

## Notes for Kato / Mike

- DB at `/home/dino/grocery/grocery.db`
- Read list: `cd /home/dino/grocery && python3 -c "import db; db.init_db(); import json; print(json.dumps(db.get_all_items(), indent=2))"`
- Add item: `db.add_item(name='milk', quantity='1', added_by='kato')`
- Katie-adjacent system — don't clear or modify without explicit instruction from Dino.
