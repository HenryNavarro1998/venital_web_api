import json
from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits


class BrandController(http.Controller):

    @route('/brand', auth='public', type='http', methods=['GET'])
    @validate_limits()
    def get_brands(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order")
        domain = []

        if "name" in kwargs:
            domain.append(("name", "ilike", kwargs["name"]))

        AutoMfgBrand = request.env["auto.mfg.brand"].sudo()
        
        data = search_paginate(
            total_items=AutoMfgBrand.search_count([]),
            page=page,
            limit=limit
        )

        items = AutoMfgBrand.search(
            domain=domain,
            offset=data.get("offset", 0), 
            limit=data.get("items_per_page"),
            order=order
        )

        data["items"] = [{
            "id": brand.id,
            "name": brand.name,
            "code": brand.code
        } for brand in items]

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

