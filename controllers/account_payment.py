from odoo import http
from odoo.http import route, request
import json

class AccountPayment(http.Controller):

    @route("/account-payment", type="json", auth="api_key", methods=["POST"], csrf=False)
    def create_payment(self, *args, **kwargs):

        data = json.loads(request.httprequest.data)

        sale = request.env["account.payment"].create({
            "partner_id": data.get("partner"),
            "amount": data.get("amount"),
            "journal_id": data.get("journal"),
            "ref": data.get("ref"),
            "currency_id": data.get("currency"),
            "date": data.get("date"),
            "payment_type": "inbound",
        })

        return {
            "name": sale.name
        }

        # return request.make_response(
        #     data=None,
        #     status=201,
        #     headers=[("Content-Type", "application/json")]
        # )