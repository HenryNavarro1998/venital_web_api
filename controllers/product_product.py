from odoo import http
from odoo.http import route, request
from .utils import search_paginate, validate_limits
import json
import base64

class ProductProduct(http.Controller):

    @route("/products", type="http", auth="api_key", methods=["GET"])
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

    if "name" in kwargs:
        name_filter = [name for name in kwargs.get("name", "").split(",")]
        domain.append(("name", "in", name_filter))

    if "code" in kwargs:
        domain.append(("default_code", "ilike", kwargs.get("code")))

    if "model" in kwargs:
        model_filter = [model for model in kwargs.get("model", "").split(",")]
        domain.append(("auto_model_ids", "in", model_filter))

    if "brand" in kwargs:
        brand_filter = [brand for brand in kwargs.get("brand", "").split(",")]
        domain.append(("product_brand_id", "in", brand_filter))

    if "year" in kwargs:
        year_filter = [year for year in kwargs.get("year", "").split(",")]
        domain.append(("auto_built_year_ids", "in", year_filter))

    if "engine" in kwargs:
        engine_filter = [engine for engine in kwargs.get("engine", "").split(",")]
        domain.append(("auto_engine_ids", "in", engine_filter))

    if "category" in kwargs:
        category_filter = [category for category in kwargs.get("category", "").split(",")]
        domain.append(("categ_id", "in", category_filter))


    return domain


def _get_product_data(product):
    prices = product.taxes_id \
        .filtered_domain([("company_id", "=", request.env.company.id)]) \
        .compute_all(price_unit=product.lst_price, product=product)

    return {
        "id": product.id,
        "name": product.name,
        "code": product.default_code,
        "priceBase": product.lst_price,
        "priceTax": round(prices.get("total_included") - product.lst_price, 2),
        "priceTotal": prices.get("total_included"),
        "available": product.qty_available,
        "available_by_location": [{
            "location": {
                "id": stock_quant.location_id.id,
                "name": stock_quant.location_id.name
            },
            "quantity": stock_quant.quantity,
        } for stock_quant in product.stock_quant_ids.filtered_domain([("location_id.usage", "=", "internal")])],
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
    