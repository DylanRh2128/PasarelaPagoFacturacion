# `app/webhooks.py`

`POST /webhooks/stripe`: verifies the Stripe signature, ignores anything that isn't
`checkout.session.completed` or that doesn't match a known, not-yet-succeeded `Payment`
(covering both "not ours" and "already processed" in one idempotent check), then generates and
stores the invoice for the ones that are genuinely new.
