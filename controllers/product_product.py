from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
import json
import base64

class ProductProduct(http.Controller):

    @route("/products", type="http", auth="user", methods=["GET"])
    def products(self, *args, **kwargs):
        res = None

        if request.httprequest.method == "GET":
            res = self._get_products(*args, **kwargs)

        return res


    @validate_limits()
    def _get_products(self, *args, **kwargs):
        page = kwargs.get("page")
        limit = kwargs.get("limit")
        order = kwargs.get("order", "")
        domain = _get_filters_domain(*args, **kwargs)

        if "reverse" in kwargs:
            order += " desc"

        ProductProduct = request.env["product.product"].sudo()

        data = search_paginate(
            total_items=ProductProduct.search_count(domain),
            page=page,
            limit=limit
        )

        items = ProductProduct.search(
            domain=domain, 
            offset=data.get("offset", 0),
            limit=data.get("items_per_page"),
            order=order
        )

        data["items"] = [_get_product_data(product) for product in items]

        return request.make_response(
            json.dumps(data),
            headers=[("Content-Type", "application/json")]
        )


#TODO: Filter by:
#   - Product ID    ✅   - Code          ✅   - Model ID      ❌
#   - Model Name    ❌   - Brand ID      ❌   - Comments      ❌
#   - Year          ❌   - Create Date   ❌   - Pricelist ID  ❌
#   - Currency ID   ❌   - Motor ID      ❌   - Category ID   ❌
#   - Available     ❌
def _get_filters_domain(*args, **kwargs):
    domain = []

    if "id" in kwargs:
        id_filter = [model for model in kwargs.get("id", "").split(",")]
        domain.append(("id", "in", id_filter))

    if "code" in kwargs:
        domain.append(("default_code", "ilike", kwargs.get("code")))

    return domain


def _get_product_data(product):
    return {
        "id": product.id,
        "name": product.name,
        "code": product.default_code,
        "price": product.lst_price,
        "priceTotal": product.lst_price,
        "category": {
            "id": product.categ_id.id,
            "name": product.categ_id.name,
        },
        "brands": [{
            "id": brand.id,
            "name": brand.name
        } for brand in product.product_tmpl_id.auto_brand_ids],
        "models": [{
            "id": model.id,
            "name": model.name,
            "code": model.code
        } for model in product.product_tmpl_id.auto_model_ids],
        "years": [{
            "id": year.id,
            "name": year.name,
        } for year in product.product_tmpl_id.auto_built_year_ids],
        "images": _get_products_images(product)
    }

def _get_products_images(product):
    img_encode = base64.b64encode
    return [
        product.image_1920 and img_encode(product.image_1920).decode(),
        *(
            p.image_1920 and img_encode(p.image_1920).decode()
            for p in product.product_template_image_ids
        )
    ]
    

    # @route("/product-product/photos", type="http", auth="user", methods=["GET"])
    # @validate_limits()
    # def get_photos(self, *args, **kwargs):
    #     page = kwargs.get("page")
    #     limit = kwargs.get("limit")
    #     order = kwargs.get("order", "")
    #     domain = []

    #     if "reverse" in kwargs:
    #         order += " desc"

    #     if "id" in kwargs:
    #         filter_id = [model for model in kwargs.get("id", "").split(",")]
    #         domain.append(("id", "in", filter_id))

    #     if "code" in kwargs:
    #         domain.append(("default_code", "ilike", kwargs.get("code")))

    #     #TODO: Filter by model, year and brand
    #     # if "model" in kwargs:
    #     #     filter_model = [model for model in kwargs.get("model", "").split(",")]
    #     #     domain.append(("product_tag_ids", "in", filter_model))
            

    #     ProductProduct = request.env["product.product"].sudo()

    #     data = search_paginate(
    #         total_items=ProductProduct.search_count(domain=domain),
    #         page=page,
    #         limit=limit
    #     )

    #     items = ProductProduct.search(
    #         domain=domain,
    #         offset=data.get("offset", 0),
    #         limit=data.get("items_per_page"),
    #         order=order
    #     )

    #     data["items"] = [{
    #         "id": product.id,
    #         "name": product.name,
    #         "code": product.default_code,
    #         "photos": [
    #             product.image_1920 and base64.b64encode(product.image_1920).decode('utf-8'),
    #             *(product_image.image_1920 and base64.b64encode(product_image.image_1920).decode('utf-8')
    #                 for product_image in product.product_template_image_ids)
    #         ]
    #     } for product in items] 

    #     return request.make_response(
    #         json.dumps(data),
    #         headers=[("Content-Type", "application/json")]
    #     )

