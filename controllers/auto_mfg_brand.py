import json
from odoo import http
from odoo.http import route, request
from .utils import search_paginate


class BrandController(http.Controller):

    @route('/brand', auth='public', type='http', methods=['GET'])
    def get_brands(self, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        domain = []

        if "name" in kwargs:
            domain.append(("name", "ilike", kwargs["name"]))

        AutoMfgBrand = request.env["auto.mfg.brand"].sudo()
        response_data = search_paginate(
            AutoMfgBrand,
            domain=domain,
            fields=["name", "code"],
            page=page,
            limit=limit
        )

        return request.make_response(
            json.dumps(response_data),
            headers=[('Content-Type', 'application/json')]
        )

