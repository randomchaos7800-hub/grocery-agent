# Grocery Agent

Shared grocery list for Dino and Katie. Currently a functional Telegram bot with basic list management and product search. Being expanded into a full AI-powered shopping assistant.

**Status: Active — limited functionality, expanding.**

---

## What It Does Now

- Shared grocery list via Telegram (Dino + Katie)
- Add, remove, check off, uncheck items by name or ID
- Free-text quick-add: type an item name, it gets added. Type a name that matches something already on the list, it gets checked off.
- `/search <query>` — headless Playwright search via DuckDuckGo for product info
- SQLite persistence (`grocery.db`)
- `/clearall` with confirmation timeout (30s)

## Current Limitations

- **Telegram only** — Telegram is deprecated across the stack. Discord migration pending.
- **No AI** — search is raw Playwright scrape, not LLM-assisted
- **No price lookup** — search returns raw page text
- **No smart suggestions** — no "you usually buy this" or "you're out of X"
- **No categories** — items are flat, no aisle/category organization
- **No cross-notification** — if Katie adds something, Dino doesn't get pinged (and vice versa)
- **No recurring items** — staples that always need restocking aren't tracked
- **No store integration** — no Walmart/Kroger/Safeway price comparison

---

## Planned Expansions

- [ ] Discord interface (replace Telegram)
- [ ] LLM-assisted search — actual product info, prices, substitutions
- [ ] Smart add — "we need breakfast stuff" → suggests items based on history
- [ ] Recurring items — staples that auto-reappear when cleared
- [ ] Categories / aisle grouping
- [ ] Cross-user notifications (Katie adds → Dino gets pinged)
- [ ] Store price comparison
- [ ] Integration with FinEngine — grocery spend tracked against weekly $150 budget
- [ ] Kato awareness — Kato can read/update the list on Dino's behalf

---

## Architecture

```
bot.py      — Telegram bot, command handlers, message routing
db.py       — SQLite layer (items table: id, name, qty, category, checked, added_by, notes)
search.py   — Playwright headless search via DuckDuckGo
grocery.db  — SQLite database (not committed)
grocery.service — systemd unit file
```

**Runtime:** Python 3.10+, venv
**Interface:** Telegram (python-telegram-bot v22)
**DB:** SQLite at `grocery/grocery.db`
**Search:** Playwright + Chromium headless

---

## Commands

| Command | Description |
|---------|-------------|
| `/add <item> [qty]` | Add item to list |
| `/remove <item or #id>` | Remove item |
| `/check <item or #id>` | Mark as checked off |
| `/uncheck <item or #id>` | Unmark |
| `/list` | Show full list (unchecked + checked) |
| `/clear` | Remove all checked items |
| `/clearall` | Wipe entire list (requires confirmation) |
| `/search <query>` | Search for product info |
| `<text>` | Quick-add item, or check off if name matches |

Items can be referenced by name (`milk`) or ID (`#12`). Partial name matching works.

---

## Setup

```bash
cd grocery
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp config/secrets.env.example config/secrets.env
# edit secrets.env: add TELEGRAM_BOT_TOKEN

cp config/settings.json.example config/settings.json
# edit settings.json: add your Telegram user IDs to allowed_telegram_users
```

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
TELEGRAM_BOT_TOKEN=your_token_here
```

### `config/settings.json`
```json
{
  "allowed_telegram_users": [123456789],
  "search": {
    "timeout_ms": 15000
  }
}
```

Get Telegram user IDs by messaging `@userinfobot` on Telegram.

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

- DB is at `/home/dino/grocery/grocery.db`
- Read list: `python3 -c "import sys; sys.path.insert(0,'~/grocery'); import db; db.init_db(); print(db.get_all_items())"`
- Add item programmatically: `db.add_item(name='milk', quantity='1', added_by='kato')`
- This is a Katie-adjacent system — treat updates carefully. Don't clear or modify without explicit instruction.
