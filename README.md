<h1 align="center">🔍 Torrent Hunt Bot (Personal Edition)</h1>

<p align="center">
A lightweight, fast, personal Telegram bot for searching torrents and getting <b>instant copyable magnet links</b> and <b>one-tap sending to your Seedr bot (@hemanthseedrobot)</b>.
</p>

---

## ✨ Features

- **⚡ Instant In-Memory Pagination & Sorting**: Results are cached in memory per search session so paging (Next/Prev) and sorting (by seeds/size/date) are instant (< 50ms) without re-querying Jackett/Prowlarr.
- **🧲 One-Tap Magnet Retrieval**: Quick-access buttons (`[ 🧲 #1 ]`, `[ 🧲 #2 ]`, ...) let you pull a magnet link directly without jumping between chats.
- **🌱 Direct Seedr Bot Integration**: Includes a direct **"🌱 Send to @hemanthseedrobot"** button that forwards the hash directly to your Seedr bot.
- **📋 Tap-to-Copy Magnet**: Magnet links are rendered inside Telegram `<code>` blocks so tapping the text copies the full link to your clipboard.
- **🧹 Multi-Tracker Deduplication**: Automatically deduplicates duplicate releases returned across multiple indexers, keeping the one with the highest seeds.
- **🛡️ 64-Byte Safe**: Uses compact session IDs in callback data to prevent Telegram's 64-byte `BUTTON_DATA_INVALID` error on long queries or non-Latin languages.
- **🐳 Docker Ready**: Persistent data volume (`./data`) ensures your Telegram session login and SQLite database survive container restarts and updates.

---

## 🔌 Supported Providers

Connects to your local or remote indexer aggregator:
- [Jackett](https://github.com/Jackett/Jackett)
- [Prowlarr](https://github.com/Prowlarr/Prowlarr)

---

## 🚀 Deployment with Docker (Recommended for Servers)

### 1. Clone & Setup Configuration
Clone the repository to your server and enter the directory:

```bash
git clone <your-repo-url> torrenthunt
cd torrenthunt
```

Copy the sample environment file to `.env`:
```bash
cp sample.env .env
```

Edit `.env` with your favorite editor (e.g., `nano .env`) and fill in:
* `BOT_TOKEN`: Obtained from [@BotFather](https://t.me/BotFather)
* `API_ID` & `API_HASH`: Obtained from [my.telegram.org](https://my.telegram.org)
* `BOT_ADMINS`: Your numeric Telegram user ID (from [@userinfobot](https://t.me/userinfobot))
* `SEEDR_BOT_USERNAME`: `hemanthseedrobot` (or your custom bot username)
* `TORRENT_PROVIDER`: `jackett` or `prowlarr`
* `JACKETT_URL` / `JACKETT_API_KEY` (or Prowlarr equivalents)

> **Note for Docker networking**: If Jackett/Prowlarr is running on the host server or another container, use `http://host.docker.internal:9117` or the container's Docker network name rather than `localhost`.

---

### 2. Run with Docker Compose

Run the bot in the background:
```bash
docker compose up -d --build
```

View the live logs:
```bash
docker compose logs -f
```

Stop the bot:
```bash
docker compose down
```

The `./data` folder on your host machine will safely store `torrenthunt.session` and `torrenthunt.db`.

---

### Alternative: Run with Standalone Docker

```bash
# Build the Docker image
docker build -t torrenthunt .

# Run container with volume mount for persistent data
docker run -d \
  --name torrenthunt \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  torrenthunt
```

---

## 💻 Running Locally (Without Docker)

### Requirements
- Python 3.12+

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp sample.env .env
# Edit .env with your credentials

# 3. Start the bot
python app/main.py
```

---

## 📖 How to Use

1. **Direct Search**: Send any search query (e.g. `Inception 1080p`) directly in the bot chat.
2. **Retrieve Magnet**:
   - Tap any `[ 🧲 #1 ]`, `[ 🧲 #2 ]` button below the results to receive the magnet link immediately.
   - Or tap the blue title link to view full details.
3. **Send to Seedr**:
   - Tap **"🌱 Send to @hemanthseedrobot"** to start the torrent immediately in your Seedr bot.
   - Or tap the `<code>magnet:...</code>` block to copy the magnet link and paste it into Seedr web / bot.
4. **Inline Search**: In any Telegram chat or group, type:
   ```
   @YourBotUsername Inception
   ```
   Or search a specific indexer:
   ```
   @YourBotUsername !1337x Inception
   ```
5. **Bookmarks**: Save torrents to your personal list and access them later by sending `/bookmarks` or typing `@YourBotUsername #bookmarks` inline.

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Telegram Bot Token from @BotFather | **Required** |
| `API_ID` | Telegram API ID from my.telegram.org | **Required** |
| `API_HASH` | Telegram API Hash from my.telegram.org | **Required** |
| `BOT_ADMINS` | Comma-separated admin Telegram user IDs | `""` |
| `SEEDR_BOT_USERNAME` | Username of your Seedr bot (without @) | `hemanthseedrobot` |
| `WORKDIR` | Directory where session & SQLite database are saved | `/app/data` |
| `DATABASE_URL` | SQLite / PostgreSQL database connection string | `sqlite:///torrenthunt.db` |
| `TORRENT_PROVIDER` | Search provider backend (`jackett` or `prowlarr`) | `jackett` |
| `JACKETT_URL` | URL of your Jackett instance | `http://localhost:9117` |
| `JACKETT_API_KEY` | API key from Jackett dashboard | `""` |
| `JACKETT_INDEXER` | Indexer to search (`all` or specific indexer name) | `all` |
| `JACKETT_TIMEOUT` | Request timeout in seconds | `40` |
| `PROWLARR_URL` | URL of your Prowlarr instance | `http://localhost:9696` |
| `PROWLARR_API_KEY`| API key from Prowlarr settings | `""` |
