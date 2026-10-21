from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.checkout import router as checkout_router
from app.db import Base, engine
from app import models  # noqa: F401 — registers models on Base before create_all
from app.payments import router as payments_router
from app.webhooks import router as webhooks_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stripe Checkout + Invoice API")
app.include_router(checkout_router)
app.include_router(webhooks_router)
app.include_router(payments_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Where Stripe Checkout sends the buyer back (CHECKOUT_SUCCESS_URL / CHECKOUT_CANCEL_URL). Landing
# here proves nothing: the success page polls the session until the webhook marks it paid, then
# returns to the portfolio's main page.
_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:16px;
font-family:-apple-system,"Segoe UI",Roboto,sans-serif;background:#0f172a;color:#e2e8f0}}
main{{max-width:460px;text-align:center}}p{{color:#94a3b8}}a{{color:#38bdf8}}</style></head>
<body><main><h1 id="title">{title}</h1><p id="msg">{message}</p>
<p><a href="/">Back to the portfolio</a></p></main><script>{script}</script></body></html>"""

_SUCCESS_SCRIPT = """
const id = new URLSearchParams(location.search).get("session_id");
const title = document.getElementById("title"), msg = document.getElementById("msg");
let tries = 0;
async function poll() {
  const res = id && await fetch("checkout-sessions/" + encodeURIComponent(id)).catch(() => null);
  const data = res && res.ok ? await res.json() : null;
  if (data && data.status === "succeeded") {
    title.textContent = "Payment confirmed";
    msg.textContent = "Stripe's webhook confirmed it and invoice " + data.invoice_number +
      " was generated. Returning to the portfolio…";
    return setTimeout(() => location.href = "/", 4000);
  }
  if (++tries < 20) return setTimeout(poll, 1500);
  msg.textContent = "Stripe hasn't confirmed the payment yet. It will be invoiced as soon as the webhook arrives.";
}
poll();
"""


@app.get("/checkout-success", response_class=HTMLResponse)
def checkout_success():
    return _PAGE.format(
        title="Payment received",
        message="Waiting for Stripe to confirm the payment…",
        script=_SUCCESS_SCRIPT,
    )


@app.get("/checkout-cancelled", response_class=HTMLResponse)
def checkout_cancelled():
    return _PAGE.format(
        title="Payment cancelled",
        message="No charge was made. Returning to the portfolio…",
        script='setTimeout(() => location.href = "/", 3000);',
    )
