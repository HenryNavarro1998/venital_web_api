from odoo import http
from odoo.http import request, route
import json

class ProductCategory(http.Controller):

    @route("/product-category", type="http", auth="api_key", methods=["GET"])
    def get_product_category(self, *args, **kwargs):

        domain = [("parent_id", "=", False)]
        ProductCategory = request.env["product.category"].sudo()

        items = [{
            "id": category.id,
            "name": category.name,
            "childs": self.get_childs(category)
        } for category in ProductCategory.search(domain)]

        return request.make_response(
            json.dumps(items),
            headers=[("Content-Type", "application/json")]
        )

    def get_childs(self, category):
        return [{
            "id": child.id,
            "name": child.name,
            "childs": self.get_childs(child)
        } for child in category.child_id]