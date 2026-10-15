# Настройки бота-сводки криптоновостей

# RSS-ленты сайтов: название -> ссылка
RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "The Block": "https://www.theblock.co/rss.xml",
    "ForkLog": "https://forklog.com/feed",
}

# Открытые TG-каналы (username без @).
# У канала должно быть включено веб-превью: проверить можно, открыв t.me/s/<username>
TG_CHANNELS = [
    "forklog",
    "incrypted",
    "cointelegraph",
    "binance_announcements",
    "whale_alert_io",
]

# Как часто делать сводку (в часах); новости берутся за этот же период
DIGEST_INTERVAL_HOURS = 2
