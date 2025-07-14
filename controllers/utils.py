from math import ceil

def search_paginate(Model, domain=None, fields=None, page=None, limit=None):
    domain = domain or []
    fields = fields or []
    total_items = Model.search_count(domain)
    if page is not None and limit is not None:
        try:
            page = int(page)
            limit = int(limit)
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return {
                "error": "Parámetros 'page' y 'limit' deben ser enteros positivos."
            }
        offset = (page - 1) * limit
        total_pages = ceil(total_items / limit) if limit else 1
        items = Model.search_read(domain, fields=fields, offset=offset, limit=limit)
    else:
        page = None
        limit = None
        total_pages = 1
        items = Model.search_read(domain, fields=fields)
    return {
        "page": page,
        "total_items": total_items,
        "total_pages": total_pages,
        "items_per_page": limit,
        "items": items
    }