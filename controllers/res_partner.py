from odoo import http
from odoo.http import route, request
from .utils import search_paginate
import json

class ResPartnerController(http.Controller):

    @route("/partner", auth="public", type="http", method=["GET"])
    def get_partners(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        domain = []

        if "created_at" in kwargs:
            domain.append([("created_at", ">=", kwargs.get("created_at"))])
        
        ResPartner = request.env["res.partner"].sudo()
        response_data = search_paginate(
            Model=ResPartner,
            domain=domain,
            fields=["name"],
            page=page,
            limit=limit
        )

        return request.make_response(
            json.dumps(response_data),
            headers=[("Content-Type", "application/json")]
        )
