# 🤖 AI Supplier Scanner

> Automatically find the cheapest digital product suppliers across 5 major marketplaces — powered by Python, Telegram Bot, and Google Gemini AI.

---

## 📁 Project Structure

```
ai_supplier_scanner/
├── main.py                    ← Entry point, starts the Telegram bot
├── requirements.txt           ← All Python dependencies
├── .env.example               ← Template for your secrets
├── scanner.log                ← Auto-generated log file
│
├── config/
│   ├── __init__.py
│   └── settings.py            ← Central config: API keys, marketplace defs, defaults
│
├── ai/
│   ├── __init__.py
│   └── gemini_client.py       ← Gemini AI: keyword extraction, summaries, profit tips
│
├── scrapers/
│   ├── __init__.py            ← Scraper registry (ALL_SCRAPERS list)
│   ├── base_scraper.py        ← Abstract base class + ProductListing dataclass
│   ├── gamsgo.py              ← gamsgo.com scraper
│   ├── ggsel.py               ← ggsel.net scraper
│   ├── plati.py               ← plati.market scraper
│   ├── peakerr.py             ← peakerr.com scraper
│   └── cdkeys.py              ← cdkeys.com scraper
│
├── core/
│   ├── __init__.py
│   ├── analyzer.py            ← Orchestrates concurrent scanning + ranking
│   ├── trust_scorer.py        ← Trust score engine (Low / Medium / High)
│   └── profit_calculator.py  ← Profit margin & ROI calculator
│
└── bot/
    ├── __init__.py
    ├── handlers.py            ← All Telegram command & message handlers
    └── formatters.py          ← Formats results into clean Telegram HTML messages
```

---

## ⚙️ Features

| Feature | Description |
|---|---|
| 🔍 Product Detection | Gemini AI extracts clean product keywords from natural language |
| 🏪 5 Marketplaces | GamsGo, GGsel, Plati Market, Peakerr, CDkeys |
| 🌐 Search Links | Always generates direct search links even if scraping is blocked |
| 🕷️ Web Scraping | Attempts to scrape real prices, titles, sellers, ratings |
| 🏆 Cheapest Finder | Identifies and highlights the lowest-cost supplier |
| ⭐ Best Value | Finds the best balance of price + trust score |
| 🟢 Trust Scores | Low / Medium / High based on platform reputation + seller rating |
| 💳 Payment Methods | Shows accepted payment types per marketplace |
| 💰 Profit Calculator | Input a sell price and get profit, margin, and ROI |
| 🤖 AI Summary | Gemini writes a buying recommendation for each scan |
| 📱 Telegram Bot | Clean, formatted, link-rich messages with HTML formatting |
| ⚡ Concurrent | All 5 marketplaces are scanned simultaneously |

---

## 🚀 Installation Guide

### Step 1 – Install Python

Requires **Python 3.11+**

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install python3.11 python3.11-pip python3.11-venv -y

# macOS (with Homebrew)
brew install python@3.11

# Windows – download from https://python.org and check "Add to PATH"
```

Verify:
```bash
python3 --version   # Should show Python 3.11.x or higher
```

---

### Step 2 – Clone / Download the Project

```bash
# If you have Git:
git clone https://github.com/your-repo/ai_supplier_scanner.git
cd ai_supplier_scanner

# Or just unzip the downloaded folder and cd into it
```

---

### Step 3 – Create a Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate it:
# Linux / macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

You should now see `(venv)` in your terminal prompt.

---

### Step 4 – Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- `python-telegram-bot` – Telegram bot framework
- `requests` + `beautifulsoup4` + `lxml` – web scraping
- `google-generativeai` – Gemini AI API
- `python-dotenv` – environment variable loading
- `aiohttp` – async HTTP
- `fake-useragent` – rotating user agents

---

### Step 5 – Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name for your bot (e.g. `AI Supplier Scanner`)
4. Choose a username (must end in `bot`, e.g. `ai_supplier_bot`)
5. BotFather will send you a **token** like:
   ```
   1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
   ```
6. **Save this token** — you'll need it in the next step.

---

### Step 6 – Get a Gemini API Key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API key"**
4. Copy the key (starts with `AIza...`)

> **Note:** Gemini has a generous free tier. AI features gracefully degrade to "disabled" if no key is provided.

---

### Step 7 – Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your favourite text editor:

```bash
nano .env   # Linux/macOS
notepad .env   # Windows
```

Fill in your values:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
GEMINI_API_KEY=AIzaSyYourKeyHere

# Optional tweaks:
REQUEST_TIMEOUT=10
MAX_RESULTS_PER_MARKET=5
```

Save and close.

---

### Step 8 – Run the Bot

```bash
python main.py
```

You should see:
```
==================================================
  AI Supplier Scanner – Starting up
  Gemini AI: ✓ enabled
==================================================
INFO  Bot is running. Press Ctrl+C to stop.
```

---

### Step 9 – Test the Bot

1. Open Telegram
2. Find your bot by its username
3. Send `/start`
4. Type any product name, for example:
   - `ChatGPT Plus`
   - `Spotify Premium`
   - `Netflix 1 month`
   - `Windows 11 Pro key`

---

## 💬 Bot Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Welcome message and instructions | `/start` |
| `/help` | Show help guide | `/help` |
| `/search <product>` | Scan all marketplaces | `/search ChatGPT Plus` |
| `/profit <product> <price>` | Scan + calculate profit at your sell price | `/profit Spotify 8.99` |
| _(any text)_ | Automatically treated as a product search | `Netflix 1 month` |

---

## 📊 Example Bot Output

```
🔍 Scan Results: ChatGPT Plus
────────────────────────────────

1. GGsel
  📦 ChatGPT Plus 1 Month Subscription
  💵 Price: $9.50
  👤 Seller: digital_shop_pro
  ⭐ Rating: 4.8/5
  🟢 Trust: High
  💳 Crypto | USDT TRC20 | Visa | Mastercard
  🔗 View listing

2. GamsGo
  📦 ChatGPT Plus Monthly
  💵 Price: $11.99
  🟢 Trust: High
  💳 Crypto | USDT TRC20 | Visa | Mastercard
  🔗 View listing

3. CDkeys
  📦 ChatGPT Plus 1 Month
  💵 Price: $12.50
  🟢 Trust: High
  💳 Visa | Mastercard | PayPal | Crypto
  🔗 View listing

────────────────────────────────
🏆 Cheapest: GGsel → $9.50
⭐ Best Value: GGsel → $9.50 (🟢 High trust)

💹 Profit Analysis
💰 Cost Price: $9.50
🏷️ Sell Price: $12.35
📈 Profit: $2.85
📊 Margin: 23.1%
🔄 ROI: 30.0%
💡 Suggested Sell Price: $12.35

🤖 AI Tip: Bundle with other subscriptions for higher perceived value.

📝 Analysis: GGsel offers the lowest price with high platform trust. 
Good resell potential on Telegram groups or local marketplaces.

🔄 Send another product name to scan again.
```

---

## 🔧 Running as a Background Service (Linux VPS)

### Option A – systemd service

Create `/etc/systemd/system/supplier_scanner.service`:

```ini
[Unit]
Description=AI Supplier Scanner Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai_supplier_scanner
ExecStart=/home/ubuntu/ai_supplier_scanner/venv/bin/python main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable supplier_scanner
sudo systemctl start supplier_scanner
sudo systemctl status supplier_scanner
```

### Option B – screen / tmux

```bash
screen -S scanner
python main.py
# Detach: Ctrl+A then D
# Reattach: screen -r scanner
```

---

## 🛠️ Customisation

### Add a new marketplace

1. Create `scrapers/mymarket.py` extending `BaseScraper`
2. Implement `_parse()` to extract listings from HTML
3. Add the scraper instance to `scrapers/__init__.py`'s `ALL_SCRAPERS` list

```python
# scrapers/mymarket.py
from scrapers.base_scraper import BaseScraper, ProductListing

class MyMarketScraper(BaseScraper):
    name = "MyMarket"
    search_url_template = "https://mymarket.com/search?q={query}"
    trust_base = 70
    payments = ["Visa", "Mastercard"]

    def _parse(self, html, query, search_url):
        soup = self._soup(html)
        # ... your parsing logic ...
        return listings
```

### Change the default profit margin

Edit `config/settings.py`:
```python
DEFAULT_MARGIN_PERCENT: float = 40.0   # 40% markup
```

### Change trust scores

Edit `PLATFORM_TRUST_SCORES` in `config/settings.py`.

---

## 🔒 Security Notes

- Never commit `.env` to Git — it's in `.gitignore`
- Keep your Telegram bot token private
- Rotate your Gemini API key if compromised
- Run on a trusted VPS with a firewall

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `TELEGRAM_BOT_TOKEN is not set` | Check your `.env` file has the token |
| Bot doesn't respond | Make sure `python main.py` is running |
| All prices are N/A | Marketplace blocked scraping – links still work |
| Gemini errors | Check your API key and quota at aistudio.google.com |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside venv |
| Slow results | Normal – concurrent scraping of 5 sites takes ~10-20s |

---

## 📦 Tech Stack

| Component | Technology |
|---|---|
| Bot framework | `python-telegram-bot` v20 (async) |
| Web scraping | `requests` + `BeautifulSoup4` + `lxml` |
| AI / NLP | Google Gemini 1.5 Flash |
| Config | `python-dotenv` |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` |
| Logging | Python stdlib `logging` |

---

## 📄 License

MIT License — free for personal and commercial use.
