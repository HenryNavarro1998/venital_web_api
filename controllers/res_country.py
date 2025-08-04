from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
from datetime import datetime
import json

class ResCountry(http.Controller):

    @route("/res-country", auth="api_key", type="http", methods=["GET"])
    @validate_limits()
    def get_partners(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        if "reverse" in kwargs:
            order += " desc"
        
        ResCountry = request.env["res.country"].sudo()
        
        data = search_paginate(
            total_items=ResCountry.search_count([]),
            page=page,
            limit=limit
        )

        items = ResCountry.search(
            domain=domain,
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order,
        )

        data["items"] = [{
            "id": country.id,
            "name": country.name,
        } for country in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )
