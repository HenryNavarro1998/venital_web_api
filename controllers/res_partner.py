from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
from datetime import datetime
import json

class ResPartnerController(http.Controller):

    @route("/partners", auth="api_key", type="http", methods=["GET"])
    @validate_limits()
    def get_partners(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        domain.extend((("parent_id", "=", False), ("type", "=", "contact")))

        if "reverse" in kwargs:
            order += " desc"

        if "name" in kwargs:
            domain.append(("name", "ilike", kwargs.get("name")))

        if "create_date" in kwargs:
            domain.append(("create_date", ">=", kwargs.get("create_date")))
        
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

        data["items"] = [
            {
                "id": partner.id,
                "name": partner.name or None,
                "document": partner.vat or None,
                "email": partner.email or None,
                "pricelist": {
                    "id": partner.property_product_pricelist.id,
                    "name": partner.property_product_pricelist.name
                },
                **self.get_address_info(partner, "main"), #addresses and phones
                "comment": partner.comment or None,
            } for partner in items
        ]


        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )

    def get_address_info(self, partner, partner_type=None):
        data = {
            "addresses": [{
                "id": partner.id,
                "type": partner_type or partner.type,
                "name": partner.name or None,
                "street": partner.street or None,
                "street2": partner.street2 or None,
                "city": partner.city or None,
                "zip": partner.zip or None,
                "state": {
                    "id": partner.state_id.id,
                    "name": partner.state_id.name,
                },
                "country": {
                    "id": partner.country_id.id,
                    "name": partner.country_id.name,
                },
            }],
            "phones": [{
                "id": partner.id,
                "phone": partner.phone or None,
                "mobile": partner.mobile or None,
            }]
        }

        for child in partner.child_ids:
            child_data = self.get_address_info(child)
            data["addresses"].extend(child_data["addresses"])
            data["phones"].extend(child_data["phones"])
        
        return data