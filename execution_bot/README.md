# Execution Bot

Receives TradingView alert webhooks and places real orders with Alpaca.

## What this is / is not

- This turns a TradingView alert into a live (or paper) order. It does not
  run any Pine Script logic itself -- your Pine strategy decides *when* to
  alert, this bot only executes *what* the alert says.
- Start with `ALPACA_PAPER=true` (Alpaca's paper-trading account, fake
  money) until you've watched it place orders correctly. Only switch to
  `false` once you trust it.

## 1. Get Alpaca API keys

1. Sign up at https://alpaca.markets (free).
2. In the dashboard, switch to **Paper Trading** and generate an API key +
   secret from there first.
3. Keep the key/secret private -- anyone with them can trade on your
   account.

## 2. Deploy this bot (Render, free tier, no computer needed)

1. Go to https://render.com and sign up (can connect your GitHub account
   directly).
2. **New -> Web Service**, pick this repository.
3. Set **Root Directory** to `execution_bot`.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Under **Environment**, add these variables (from `.env.example`):
   - `ALPACA_API_KEY`
   - `ALPACA_SECRET_KEY`
   - `ALPACA_PAPER` = `true`
   - `WEBHOOK_SECRET` = make up a long random string yourself -- this is
     what stops anyone else from calling your webhook and placing orders
     on your account.
7. Deploy. Render gives you a URL like `https://your-bot.onrender.com`.
8. Visit `https://your-bot.onrender.com/health` -- it should return
   `{"status":"ok","paper_trading":true}`.

## 3. TradingView alert setup

Requires at least TradingView's paid **Essential** plan -- the webhook URL
field on alerts is not available on the free Basic plan.

When creating an alert from one of this repo's strategies:

- **Webhook URL**: `https://your-bot.onrender.com/webhook`
- **Message** (JSON):

```json
{
  "secret": "the WEBHOOK_SECRET you set in Render",
  "symbol": "{{ticker}}",
  "action": "buy",
  "qty": 10
}
```

Fields:
- `action`: `"buy"`, `"sell"`, or `"close"` (closes the whole position in
  that symbol).
- `qty`: number of shares. Or use `notional` (dollar amount) instead of
  `qty` if you'd rather size by dollars.
- `limit_price`: optional -- omit it for a market order, include it for a
  limit order.

You'll want one alert per entry/exit condition in your strategy, each with
its own hardcoded `action` (and `qty`/`notional`) in the message.

## 4. Going live

Once paper trading looks correct: generate a **live** API key/secret from
the Alpaca dashboard (not the paper ones), swap `ALPACA_API_KEY` /
`ALPACA_SECRET_KEY` in Render, and set `ALPACA_PAPER=false`. Real orders
will place from that point on.
