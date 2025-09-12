from odoo import http
from odoo.http import route, request
from odoo.exceptions import UserError
import json

class SaleOrder(http.Controller):

    @route("/sale-order", type="json", auth="api_key", methods=["POST"], csrf=False)
    def create_order(self, *args, **kwargs):
        
        data = json.loads(request.httprequest.data)
        
        res = self.process_sale(data)
        res["payments"] = self.create_payment(data.get("partner"), data.get("payments"))

        return res


    @route("/sale-order/refund", type="json", auth="api_key", methods=["POST"], csrf=False)
    def refund_order(self, *args, **kwargs):
        data = json.loads(request.httprequest.data)

        sale = request.env["sale.order"].browse(data["id"])

        
        picking = request.env["stock.picking"].create({
            "sale_id": sale.id,
            "partner_id": sale.partner_shipping_id.id,
            "picking_type_id": request.env.ref("stock.picking_type_in").id,
            "location_id": request.env.ref("stock.stock_location_suppliers").id,
            "location_dest_id": request.env.ref("stock.stock_location_stock").id,
            "move_ids": [(0,0,{
                "name": line["product"].get("name"),
                "product_id": line["product"].get("id"),
                "quantity": line["quantity"],
                "location_id": request.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": request.env.ref("stock.stock_location_stock").id,
            }) for line in data.get("lines")]
        })

        return {
            "id": picking.id,
            "name": picking.name
        }

        

        # self.refund_pickings(sale)


    def refund_picking(self, sale):
        pass


    
    def process_sale(self, data):
        sale = request.env["sale.order"].create({
            "partner_id": data.get("partner"),
            "partner_shipping_id": data.get("delivery_address") or data.get("partner"),
            "partner_invoice_id": data.get("invoice_address") or data.get("delivery_address") or data.get("partner"),
            "pricelist_id": data.get("pricelist"),
            "order_line": [(0, 0, {
                "product_id": line["product"],
                "product_uom_qty": line["quantity"],
            }) for line in data.get("order_lines", [])]
        })

        sale._recompute_prices()
        sale.action_confirm()

        return {
            "id": sale.id,
            "name": sale.name,
            "partner": {
                "id": sale.partner_id.id,
                "name": sale.partner_id.name,
            },
            "deliveryAddress": {
                "id": sale.partner_shipping_id.id,
                "name": sale.partner_shipping_id.name,
            },
            "orderLines": [{
                "product": {
                    "id": line.product_id.id,
                    "name": line.product_id.name,
                },
                "quantity": line.product_uom_qty,
                "priceUnit": line.price_subtotal,
                "subtotal": line.price_subtotal,
                "tax": line.price_tax,
                "total": line.price_total,
            } for line in sale.order_line],
            "amountUntaxed": sale.amount_untaxed,
            "amountTax": sale.amount_tax,
            "amountTotal": sale.amount_total,
        }

    def create_payment(self, partner, payments_data):
        payments = request.env["account.payment"].create([{
            "partner_id": partner,
            "amount": data.get("amount"),
            "journal_id":  data.get("journal"),
            "date": data.get("date"),
            "ref": data.get("ref"),
            "payment_type": "inbound"
        } for data in payments_data])

        payments.action_post()

        return [{
            "name": payment.name,
            "partner_id": {
                "id": payment.partner_id.id,
                "name": payment.partner_id.name,
            },
            "journal_id": {
                "id": payment.journal_id.id,
                "name": payment.journal_id.name,
            },
            "amount": payment.amount,
            "date": payment.date,
            "ref": payment.ref,
        } for payment in payments]