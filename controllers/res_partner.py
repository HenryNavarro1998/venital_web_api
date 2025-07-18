from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
from datetime import datetime
import json

class ResPartnerController(http.Controller):

    @route("/res-partner", auth="user", type="http", methods=["GET"])
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

        data["items"] = [{
            "id": partner.id,
            "name": partner.name,
            "document": partner.vat,
            "email": partner.email,
            "pricelist": {
                "id": partner.property_product_pricelist.id,
                "name": partner.property_product_pricelist.name
            },
            "addresses": [
                {
                    "id": partner.id,
                    "type": "main",
                    "name": partner.name,
                    "street": partner.street,
                    "street2": partner.street2,
                    "city": partner.city,
                    "zip": partner.zip,
                    "phone": partner.phone,
                    "mobile": partner.mobile,
                    "state": {
                        "id": partner.state_id.id,
                        "name": partner.state_id.name,
                    },
                    "country": {
                        "id": partner.country_id.id,
                        "name": partner.country_id.name,
                    },
                },
            ] + self.get_addresses(partner),
            "comment": partner.comment
        } for partner in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )


    def get_addresses(self, partner):

        address_list = []
        for address in partner.child_ids:
            address_list.extend([{
            "id": address.id,
            "type": address.type,
            "name": address.name,
            "street": address.street,
            "street2": address.street2,
            "city": address.city,
            "zip": address.zip,
            "phone": address.phone,
            "mobile": address.mobile,
            "state": {
                "id": address.state_id.id,
                "name": address.state_id.name,
            },
            "country": {
                "id": address.country_id.id,
                "name": address.country_id.name,
            },
        }])

            address_list.extend(self.get_addresses(address))

        return address_list
