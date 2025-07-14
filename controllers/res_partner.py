from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
import json

class ResPartnerController(http.Controller):

    @route("/partner", auth="user", type="http", methods=["GET"])
    @validate_limits()
    def get_partners(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        if "reverse" in kwargs:
            order += " desc"

        if "create_date" in kwargs:
            date  = kwargs.get("create_date")
            domain.append([("create_date", ">=", kwargs.get("create_date"))])
        
        ResPartner = request.env["res.partner"].sudo()
        
        data = search_paginate(
            total_items=ResPartner.search_count([]),
            page=page,
            limit=limit
        )

        items = ResPartner.search(
            domain=domain,
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order,
        )

        data["items"] = [{
            "id": partner.id,
            "name": partner.name,
            "document": partner.vat
        } for partner in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )
