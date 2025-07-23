from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
from datetime import datetime
import json

class ResCountryState(http.Controller):

    @route("/res-country-state", auth="user", type="http", methods=["GET"])
    @validate_limits()
    def get_partners(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        if "reverse" in kwargs:
            order += " desc"
        
        ResCountryState = request.env["res.country.state"].sudo()
        
        data = search_paginate(
            total_items=ResCountryState.search_count([]),
            page=page,
            limit=limit
        )

        items = ResCountryState.search(
            domain=domain,
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order,
        )

        data["items"] = [{
            "id": state.id,
            "name": state.name,
            "country": {
                "id": state.country_id.id,
                "name": state.country_id.name
            }
        } for state in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )
