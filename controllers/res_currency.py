from odoo import http
from odoo.http import route, request
from datetime import datetime
from .utils import search_paginate, validate_limits
import json

class ResCurrency(http.Controller):

    @route("/res-currency", auth="api_key", type="http", methods=["GET"])
    @validate_limits()
    def get_currencies(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        if "reverse" in kwargs:
            order += " desc"
        
        ResCurrency = request.env["res.currency"].sudo()
        
        data = search_paginate(
            total_items=ResCurrency.search_count([]),
            page=page,
            limit=limit
        )

        items = ResCurrency.search(
            domain=domain,
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order,
        )

        data["items"] = [{
            "id": currency.id,
            "name": currency.name,
            "symbol": currency.symbol,
        } for currency in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )

    @route("/res-currency-rate", auth="api_key", type="http", methods=["GET"])
    def get_currency_rates(self, *args, **kwargs):
        
        domain = []

        if "company_id" in kwargs:
            domain.append(("company_id", "=", kwargs.get("company_id")))
            
        if "currency_id" in kwargs:
            domain.append(("currency_id", "=", kwargs.get("currency_id")))
        
        if "from_date" in kwargs:
            domain.append(("name",">=", kwargs.get("from_date")))
        
        if "to_date" in kwargs:
            domain.append(("name", "<=", kwargs.get("to_date")))
        
        ResCurrencyRate = request.env["res.currency.rate"].sudo()

        items = ResCurrencyRate.search(
            domain=domain,
            order="name desc",
        )

        data = [{
            "currency": {
                "id": rate.currency_id.id,
                "name": rate.currency_id.name
            },
            "date": rate.name.strftime("%Y/%m/%d")
                    if rate.name else False,
            "rate": rate.company_rate,
            
        } for rate in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )