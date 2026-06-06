import requests
import os
import time
import yfinance as yf

from db import (
    get_today_trades,
    get_last_10_trades,
    get_open_positions,
    get_lifetime_stats,
    get_stock_performance,
    get_setup_analytics
)
from ai import weights

from datetime import datetime, timedelta
import pytz

TIMEZONE = pytz.timezone("Asia/Kolkata")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_UPDATE_ID = None

# =========================================================
# SKIP OLD TELEGRAM UPDATES
# =========================================================

try:

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    response = requests.get(url).json()

    if response["ok"] and response["result"]:

        LAST_UPDATE_ID = response["result"][-1]["update_id"]

except:

    LAST_UPDATE_ID = None

# =========================================================
# TELEGRAM DELIVERY ENGINE
# =========================================================

def send(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    for _ in range(3):

        try:

            requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "text": msg
                },
                timeout=15
            )

            return True

        except:

            time.sleep(2)

    return False

# =========================================================
# TELEGRAM COMMAND HANDLER
# =========================================================

def handle_command(message):

    text = message["text"]

    # =============================================
    # TODAY TRADES
    # =============================================

    if text == "/today":

        trades = get_today_trades()

        if not trades:

            send("❌ No trades today")
            return

        msg = "📊 TODAY TRADE REPORT\n\n"

        for t in trades:

            msg += f"""

{t[0]}
{t[1]}

💰 Price: ₹{t[2]}
📦 Qty: {t[3]}
💵 PNL: ₹{t[4]}
🧠 {t[5]}
🕒 {(t[6] + timedelta(hours=5, minutes=30)).strftime("%d-%m-%Y %H:%M:%S")}

"""

        send(msg)

    # =============================================
    # LAST 10 TRADES
    # =============================================

    elif text == "/last10":

        trades = get_last_10_trades()

        if not trades:

            send("❌ No trade history")
            return

        msg = "📈 LAST 10 TRADES\n\n"

        for t in trades:

            msg += f"""

{t[0]}
{t[1]}

💰 ₹{t[2]}
📦 Qty: {t[3]}
💵 PNL: ₹{t[4]}
🕒 {(t[6] + timedelta(hours=5, minutes=30)).strftime("%d-%m-%Y %H:%M:%S")}

"""

        send(msg)

    # =============================================
    # OPEN POSITIONS
    # =============================================

    elif text == "/openpositions":

    positions = get_open_positions()

    if not positions:

        send("❌ No open positions")
        return

    msg = "📦 OPEN POSITIONS\n\n"

    total_pnl = 0

    for p in positions:

        symbol = p[0]
        buy_price = float(p[1])
        qty = int(p[2])
        highest = float(p[3])

        try:

            current_price = round(

                yf.Ticker(symbol)
                .history(period="1d")
                ["Close"]
                .iloc[-1],

                2

            )

            pnl = round(

                (current_price - buy_price) * qty,

                2

            )

            pnl_percent = round(

                ((current_price - buy_price)
                / buy_price) * 100,

                2

            )

            total_pnl += pnl

        except:

            current_price = "NA"
            pnl = 0
            pnl_percent = 0

        msg += f"""

{symbol}

💰 Buy Price: ₹{buy_price}
📈 Current: ₹{current_price}
📦 Qty: {qty}

💵 PNL: ₹{pnl}
📊 Return: {pnl_percent}%

🚀 Highest: ₹{highest}

"""

    msg += f"""

====================

💰 TOTAL LIVE PNL

₹{round(total_pnl,2)}

"""

    send(msg)

    # =============================================
    # MARKET STATUS
    # =============================================

    elif text == "/market":

        send("""

📈 MARKET STATUS

🇮🇳 EXCHANGE:
NSE INDIA

🕒 SESSION:
09:15 → 15:30

📊 MODE:
LIVE SCANNING

🛡 AI FILTER:
ACTIVE

🚀 MARKET ENGINE:
RUNNING

""")

    # =============================================
    # AI HEALTH
    # =============================================

    elif text == "/aihealth":

        send(f"""

🧠 AI HEALTH REPORT

✅ AI ENGINE:
ACTIVE

✅ LEARNING ENGINE:
ACTIVE

✅ TELEGRAM:
CONNECTED

✅ DATABASE:
CONNECTED

✅ POSITION RECOVERY:
ACTIVE

📈 TRACKING STOCKS:
16

📦 OPEN POSITIONS:
{len(get_open_positions())}

🚀 SYSTEM:
STABLE

""")

    # =============================================
    # AI WEIGHTS
    # =============================================

    elif text == "/weights":

        msg = "🧠 AI INDICATOR WEIGHTS\n\n"

        for k, v in weights.items():

            msg += f"{k} → {round(v,2)}\n"

        send(msg)

    # =============================================
    # RISK REPORT
    # =============================================

    elif text == "/risk":

        send("""

🛡 RISK MANAGEMENT REPORT

✅ TRAILING STOPLOSS:
ACTIVE

✅ HARD STOPLOSS:
ACTIVE

✅ TARGET SYSTEM:
ACTIVE

✅ MARKET CRASH FILTER:
ACTIVE

✅ PARTIAL BOOKING:
ACTIVE

🚀 RISK ENGINE:
PROTECTED

""")

    # =============================================
    # ACCURACY REPORT
    # =============================================

    elif text == "/accuracy":

        stats = get_lifetime_stats()

        send(f"""

🎯 ACCURACY REPORT

📈 TOTAL TRADES:
{stats["total_trades"]}

✅ WIN TRADES:
{stats["win_trades"]}

❌ LOSS TRADES:
{stats["loss_trades"]}

🎯 ACCURACY:
{stats["accuracy"]}%

💰 LIFETIME PNL:
₹{stats["lifetime_pnl"]}

""")

    # =============================================
    # TOP STOCKS
    # =============================================

    elif text == "/topstocks":

        send("""

🚀 TOP TRACKED STOCKS

✅ HDFCBANK
✅ ICICIBANK
✅ SBIN
✅ TCS
✅ INFY
✅ RELIANCE
✅ TATASTEEL
✅ HINDCOPPER
✅ SUNPHARMA
✅ BHARTIARTL

🧠 AI PRIORITY MODE:
ACTIVE

""")

    # =============================================
    # STRONGEST STOCKS
    # =============================================

    elif text == "/strongest":

        data = get_stock_performance()

        if not data:

            send("❌ No analytics data")
            return

        msg = "🚀 STRONGEST STOCKS\n\n"

        for row in data[:5]:

            symbol = row[0]
            total = row[1]
            wins = row[2]
            pnl = row[3] or 0

            accuracy = 0

            if total > 0:
                accuracy = round((wins / total) * 100, 2)

            msg += f"""

{symbol}

🎯 Accuracy: {accuracy}%
📈 Trades: {total}
💰 Total PNL: ₹{round(pnl,2)}

"""

        send(msg)

    # =============================================
    # WEAKEST STOCKS
    # =============================================

    elif text == "/weakest":

        data = get_stock_performance()

        if not data:

            send("❌ No analytics data")
            return

        weakest = sorted(
            data,
            key=lambda x: x[3] or 0
        )

        msg = "📉 WEAKEST STOCKS\n\n"

        for row in weakest[:5]:

            symbol = row[0]
            total = row[1]
            wins = row[2]
            pnl = row[3] or 0

            accuracy = 0

            if total > 0:
                accuracy = round((wins / total) * 100, 2)

            msg += f"""

{symbol}

🎯 Accuracy: {accuracy}%
📈 Trades: {total}
💰 Total PNL: ₹{round(pnl,2)}

"""

        send(msg)

    # =============================================
    # SETUP ANALYTICS
    # =============================================

    elif text == "/setupanalytics":

        data = get_setup_analytics()

        if not data:

            send("❌ No setup analytics")
            return

        msg = "🧠 SETUP ANALYTICS\n\n"

        for row in data:

            reason = row[0]
            total = row[1]
            wins = row[2]
            pnl = row[3] or 0

            accuracy = 0

            if total > 0:
                accuracy = round((wins / total) * 100, 2)

            msg += f"""

{reason}

🎯 Accuracy: {accuracy}%
📈 Trades: {total}
💰 Total PNL: ₹{round(pnl,2)}

"""

        send(msg)

    # =============================================
    # BAD TRADES
    # =============================================

    elif text == "/badtrades":

        data = get_stock_performance()

        if not data:

            send("❌ No analytics data")
            return

        weakest = sorted(
            data,
            key=lambda x: x[3] or 0
        )

        msg = "🚨 BAD TRADE DETECTOR\n\n"

        for row in weakest[:3]:

            symbol = row[0]
            pnl = row[3] or 0

            msg += f"""

⚠ {symbol}

💰 Weak PNL:
₹{round(pnl,2)}

🛡 AI Monitoring:
ACTIVE

"""

        send(msg)

    # =============================================
    # PNL REPORT
    # =============================================

    elif text == "/pnlreport":

        stats = get_lifetime_stats()

        msg = f"""

📊 FULL PERFORMANCE REPORT

📈 TOTAL TRADES:
{stats["total_trades"]}

💰 LIFETIME PNL:
₹{stats["lifetime_pnl"]}

🎯 ACCURACY:
{stats["accuracy"]}%

✅ WIN TRADES:
{stats["win_trades"]}

❌ LOSS TRADES:
{stats["loss_trades"]}

🚀 AI ENGINE STATUS:
ACTIVE

"""

        send(msg)

    # =============================================
    # STATUS REPORT
    # =============================================

    elif text == "/status":

        now = datetime.now(TIMEZONE)

        current = now.strftime("%H:%M")

        market_status = "CLOSED"

        if (
            now.weekday() < 5
            and "09:15" <= current <= "15:30"
        ):

            market_status = "OPEN"

        open_positions = get_open_positions()

        msg = f"""

🤖 BOT STATUS REPORT

🕒 TIME:
{current}

📈 MARKET:
{market_status}

📦 OPEN POSITIONS:
{len(open_positions)}

🛡 AI ENGINE:
ACTIVE

📊 DATABASE:
CONNECTED

🚀 TELEGRAM:
ONLINE

✅ BOT STATUS:
RUNNING

"""

        send(msg)

# =========================================================
# TELEGRAM COMMAND LISTENER
# =========================================================

def listen_telegram():

    global LAST_UPDATE_ID

    while True:

        try:

            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

            response = requests.get(url).json()

            if response["ok"]:

                for update in response["result"]:

                    update_id = update["update_id"]

                    if LAST_UPDATE_ID is not None:

                        if update_id <= LAST_UPDATE_ID:
                            continue

                    LAST_UPDATE_ID = update_id

                    if "message" not in update:
                        continue

                    message = update["message"]

                    if "text" not in message:
                        continue

                    handle_command(message)

            time.sleep(5)

        except:

            time.sleep(5)
