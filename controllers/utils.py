from ast import arg
from math import ceil
from odoo.http import request
import json

def search_paginate(total_items, page=None, limit=None):
    if page and limit:
        page = int(page)
        limit = int(limit)
        
        offset = (page - 1) * limit
        total_pages = ceil(total_items / limit) if limit else 1
        # items = Model.search_read(domain, fields=fields, offset=offset, limit=limit)
    else:
        page = limit = offset = None
        total_pages = 1
        # items = Model.search_read(domain, fields=fields)
    return {
        "page": page,
        "total_items": total_items,
        "total_pages": total_pages,
        "items_per_page": limit,
        "offset": offset
    }

def validate_limits():
    def wrapper(endpoint):
        def func(*args, **kwargs):
            try:
                page = kwargs.get("page")
                limit = kwargs.get("limit")
                if page and int(page) < 1 or limit and int(limit) < 1:
                    raise ValueError
            except Exception:
                return request.make_response(
                    json.dumps({"error": "Paginación inválida"}),
                    headers=[("Content-Type", "application/json")],
                    status=400
                )
            return endpoint(*args, **kwargs)
        return func
    return wrapper