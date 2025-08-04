from collections import defaultdict
from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
from datetime import datetime
import json

class AccountJournal(http.Controller):

    @route("/account-journal", auth="api_key", type="http", methods=["GET"])
    @validate_limits()
    def get_partners(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        domain.append(("type", "in", ["bank", "cash"]))

        if "reverse" in kwargs:
            order += " desc"


        if "id" in kwargs:
            domain.append(("id", "=", kwargs.get("id")))


        if "name" in kwargs:
            domain.append(("name", "ilike", kwargs.get("name")))


        if "company_id" in kwargs:
            domain.append(("company_id", "=", kwargs.get("company_id")))


        AccountJournal = request.env["account.journal"].sudo()
        
        data = search_paginate(
            total_items=AccountJournal.search_count([]),
            page=page,
            limit=limit
        )

        items = AccountJournal.search(
            domain=domain,
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order,
        )

        data["items"] = [{
            "id": journal.id,
            "name": journal.name,
        } for journal in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )


