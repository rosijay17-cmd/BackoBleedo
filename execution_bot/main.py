import hmac
import logging
import os

from fastapi import FastAPI, HTTPException, Request
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("execution_bot")

app = FastAPI()

ALPACA_API_KEY = os.environ["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]
ALPACA_PAPER = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=ALPACA_PAPER)


@app.get("/health")
def health():
    return {"status": "ok", "paper_trading": ALPACA_PAPER}


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    secret = payload.get("secret", "")
    if not hmac.compare_digest(secret, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="bad secret")

    symbol = payload.get("symbol")
    action = payload.get("action")
    if not symbol or action not in ("buy", "sell", "close"):
        raise HTTPException(status_code=400, detail="symbol and action (buy/sell/close) are required")

    logger.info("alert received: %s %s qty=%s notional=%s", action, symbol, payload.get("qty"), payload.get("notional"))

    if action == "close":
        trading_client.close_position(symbol)
        return {"status": "close_submitted", "symbol": symbol}

    side = OrderSide.BUY if action == "buy" else OrderSide.SELL
    is_crypto = "/" in symbol
    time_in_force = TimeInForce.GTC if is_crypto else TimeInForce.DAY

    qty = payload.get("qty")
    notional = payload.get("notional")
    if not qty and not notional:
        raise HTTPException(status_code=400, detail="either qty or notional is required for buy/sell")

    limit_price = payload.get("limit_price")
    if limit_price:
        order_request = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            notional=notional if not qty else None,
            side=side,
            time_in_force=time_in_force,
            limit_price=limit_price,
        )
    else:
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            notional=notional if not qty else None,
            side=side,
            time_in_force=time_in_force,
        )

    order = trading_client.submit_order(order_request)
    logger.info("order submitted: id=%s symbol=%s side=%s status=%s", order.id, order.symbol, order.side, order.status)

    return {"status": "order_submitted", "order_id": str(order.id), "symbol": symbol, "side": action}
