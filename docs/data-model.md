# Data Model

## `customers`

| column     | type     | notes   |
|------------|----------|---------|
| id         | int, PK  |         |
| email      | string   | unique  |
| created_at | datetime |         |

## `payments`

| column                     | type     | notes                                   |
|----------------------------|----------|-------------------------------------------|
| id                         | int, PK  |                                          |
| customer_id                | int, FK  | → `customers.id`                        |
| stripe_checkout_session_id | string   | unique — used to find the payment from a webhook and for idempotency |
| product_id                 | string   | key into `app/products.py`'s catalog    |
| amount_cents               | int      | copied from the catalog at checkout time, never from the client |
| currency                   | string   |                                          |
| status                     | string   | `pending` / `succeeded`                 |
| created_at                 | datetime |                                          |

## `invoices`

| column         | type     | notes                              |
|----------------|----------|--------------------------------------|
| id             | int, PK  |                                    |
| payment_id     | int, FK  | → `payments.id`, unique (one invoice per payment) |
| invoice_number | string   | `INV-{payment_id:06d}`, unique     |
| pdf_bytes      | bytea    | the generated PDF itself           |
| created_at     | datetime |                                    |
