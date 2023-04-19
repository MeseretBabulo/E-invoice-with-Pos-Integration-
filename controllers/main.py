from odoo import http
from odoo.http import request


class Sale(http.Controller):

    @http.route('/my_sale_details', type='json', auth='public', csfr=False)
    def sale_details(self, **kwargs):
        sales = []

        move_details = request.env['pos.order'].sudo().search([])
        for move in move_details:
            vals = {
                'id': move.id,
                'shop_name': move.name,
                'date_order': move.date_order,
                'customer_name': move.partner_id.name,
                'amount_total': move.amount_total,
                'amount_tax': move.amount_tax,
                'amount_paid': move.amount_paid,
                'amount_return': move.amount_return,

            }
            sales.append(vals)
        return sales
