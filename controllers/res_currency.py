from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
from datetime import datetime
import json

class ResCurrency(http.Controller):

    @route("/res-currency", auth="user", type="http", methods=["GET"])
    @validate_limits()
    def get_partners(self, **kwargs):
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
