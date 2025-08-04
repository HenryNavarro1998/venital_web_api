from collections import defaultdict
from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
from datetime import datetime
import json

class AccountMove(http.Controller):

    @route("/account-move", auth="api_key", type="http", methods=["GET"])
    @validate_limits()
    def get_partners(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        if "reverse" in kwargs:
            order += " desc"


        if "id" in kwargs:
            domain.append(("id", "=", kwargs.get("id")))


        if "name" in kwargs:
            domain.append(("name", "ilike", kwargs.get("name")))


        if "company_id" in kwargs:
            domain.append(("company_id", "=", kwargs.get("company_id")))


        if "move_type" in kwargs:
            domain.append(("move_type", "=", kwargs.get("move_type")))


        if "partner_id" in kwargs:
            domain.append(("partner_id", "=", kwargs.get("partner_id")))


        if "state" in kwargs:
            domain.append(("state", "=", kwargs.get("state")))
        

        AccountMove = request.env["account.move"].sudo()
        
        data = search_paginate(
            total_items=AccountMove.search_count([]),
            page=page,
            limit=limit
        )

        items = AccountMove.search(
            domain=domain,
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order,
        )

        data["items"] = [{
            "id": move.id,
            "name": move.name,
            "type": move.move_type,
            "invoice_date": move.invoice_date.strftime("%Y/%m/%d") 
                            if move.invoice_date else False,
            "invoice_due_date": move.invoice_date_due.strftime("%Y/%m/%d")
                            if move.invoice_date_due else False,
            "state": move.state,
            "payment_state": move.payment_state,
            "amount_untaxed": move.amount_untaxed,
            "amount_tax": move.amount_tax,
            "amount_total": move.amount_total,
            "company": {
                "id": move.company_id.id,
                "name": move.company_id.name,
            },
            "partner": {
                "id": move.partner_id.id,
                "name": move.partner_id.name
            },
            "currency": {
                "id": move.currency_id.id,
                "name": move.currency_id.name,
            },
            "invoice_lines": [{
                "product": {
                    "id": invoice_line.product_id.id,
                    "name": invoice_line.product_id.name,
                },
                "quantity": invoice_line.quantity,
                "price": invoice_line.price_unit
            } for invoice_line in move.invoice_line_ids],
            "payments": [{
                "id": partial_aml["aml"].move_id.id,
                "name": partial_aml["aml"].move_id.name,
                "ref": partial_aml["aml"].move_id.ref,
                "amount": partial_aml["amount"],
                "date": partial_aml["aml"].move_id.date.strftime("%Y/%m/%d") 
                        if partial_aml["aml"].move_id.date else False,
                "currency": {
                    "id": partial_aml["currency"].id,
                    "name": partial_aml["currency"].name,
                },
            } for partial_aml in move._get_all_reconciled_invoice_partials()],
            "taxes": self.get_taxes(move)
        } for move in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )


    def get_taxes(self, move):
        res = []
        all_taxes = move.mapped("invoice_line_ids.tax_ids")

        for tax in all_taxes:

            tax_acum = {
                "id": tax.id,
                "name": tax.name,
                "percent": tax.amount,
                "amount_base": 0,
                "amount": 0
            }

            for line in move.invoice_line_ids.filtered(lambda l: tax in l.tax_ids):
                tax_acum["amount_base"] += line.price_subtotal
                tax_acum["amount"] += line.price_subtotal * tax.amount / 100

            res.append(tax_acum)

        return res
