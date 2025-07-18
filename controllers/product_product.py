from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
import json

class ProductProduct(http.Controller):

    @route("/product-product", type="http", auth="user", methods=["GET"])
    @validate_limits()
    def get_products(self, *args, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = []

        if "reverse" in kwargs:
            order += " desc"

        ProductProduct = request.env["product.product"].sudo()

        data = search_paginate(
            total_items=ProductProduct.search_count([]),
            page=page,
            limit=limit
        )

        items = ProductProduct.search(
            domain=domain, 
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order
        )

        data["items"] = [{
            "id": product.id,
            "name": product.name,
            "code": product.default_code
        } for product in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )
