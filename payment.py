import config

from pyCryptoPayAPI import pyCryptoPayAPI

client = pyCryptoPayAPI(api_token=config.pyCryptoToken)

def create_order(payload, price):
    invoice = client.create_invoice(
        asset='USDT',
        amount=float(price),
        hidden_message='Перейдите в бота и получите ссылку на ваш товар.',
        paid_btn_name='openBot',
        paid_btn_url=f'http://t.me/simsim7_bot?start=payload={payload}',
        payload=payload,
        allow_comments=False,
        expires_in=360
    )
    return invoice

def get_invoice(invoice_id):
    invoice_data = client.get_invoices(
        invoice_ids=f"{invoice_id}"
    )
    return invoice_data['items']
