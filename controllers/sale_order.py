from odoo import http
from odoo.http import route, request
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

        sale_order = request.env["sale.order"].browse(data["id"])
        picking = sale_order.picking_ids.filtered(lambda p: p.state == "done" and p.picking_type_id.code == 'outgoing')


        return_wizard = request.env["stock.return.picking"].with_context(active_id=picking.id).create({
            "picking_id": picking.id
        })

        return_lines = []
        for line in data.get("lines"):
            return_lines.append((0,0,{
                "move_id": picking.id,
                "product_id": line["product"],
                "quantity": line["quantity"]
            }))

        return_wizard.product_return_moves = return_lines
        return_picking_id = return_wizard.create_returns()
        return_picking = request.env["stock.picking"].browse(return_picking_id)
        return {
            "name": return_picking.name
        }



    
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