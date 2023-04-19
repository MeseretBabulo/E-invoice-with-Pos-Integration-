from odoo import fields, models, api, _
import requests
import xmlrpc.client
import logging
import urllib3
import json
import pprint
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)



class PosPurchase(models.Model):
    _name = 'pos.purchase'

    is_purchase = fields.Boolean(string='purchase')
    vendor = fields.Char(string='Vendor',  readonly=True)
    name = fields.Char(string='Order Ref',  readonly=True, copy=False, default='/')
    seller_tin = fields.Char(string='Vendor Tin',  readonly=True)
    payment_means = fields.Char(string='Payment Method',  readonly=True)
    payment_term = fields.Char(string='Payment Terms',  readonly=True)
    date_order = fields.Datetime(string='Date',  index=True, default=fields.Datetime.now)
    amount_tax = fields.Float(string='Taxes', digits=0, readonly=True)
    amount_total = fields.Float(string='Total', digits=0, readonly=True)
    amount_paid = fields.Float(string='Paid',readonly=True, digits=0)
    amount_return = fields.Float(string='Returned', digits=0, readonly=True)
    lines = fields.One2many('pos.purchase.line', 'pos_purchase', string='Order Lines',
                            readonly=True, copy=True)
    note = fields.Text(string='Internal Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted')], default='draft', string="Status")
    journal_id = fields.Many2one('account.journal', string='Journal', 
                                 readonly=True, states={'draft': [('readonly', False)]}, tracking=True, store=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict')

    def post(self):
        all_move_vals = []
        move_vals = {
            #'date': self.payment_date,
            'move_type': 'in_refund',
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'currency_id': self.journal_id.currency_id.id or self.company_id.currency_id.id,
            'partner_id': 1,
            'operating_unit_id': self.journal_id.operating_unit_id.id,
            'state': 'draft',

            'line_ids': [
                (0, 0, {
                    'name': self.company_id.partner_id.property_account_receivable_id.name,
                    'debit': self.amount_total,
                    'credit': 0.0,
                    'account_id': self.company_id.partner_id.property_account_receivable_id.id,
                    'payment_id': self.id,
                    'exclude_from_invoice_tab': True,

                }),

            ],
        }
        for order_line in self.lines:
            acc = self.env['product.product'].search([('id', '=', order_line.product_id.id)
                                                      ]).property_account_expense_id
            move_vals['line_ids'].append(
                (0, 0, {
                    'name': acc.name,
                    'debit': 0.0,
                    'credit': self.amount_total,
                    'account_id': acc.id,
                    'payment_id': self.id,
                    'exclude_from_invoice_tab': False,
                    #'tax_ids': [(6, 0, order_line.tax_id.ids)],
                })

            )


        all_move_vals.append(move_vals)
        # raise UserError(
        #     _(str(move_vals)))
        self.env['account.move'].sudo().create(move_vals)
        self.state = 'posted'

    def receive(self):
        _logger.info("############## Invoice Receive###############")
        buyer_id = "Test_camp"#self.env.user.company_id.name 
        data = {}
        payload = json.dumps(data)
        url = "https://invoice-buyer.api.qa.addissystems.et/InvoiceBuyer/"+f"{buyer_id}"
        _logger.info(url)
        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'

                }
        # try:

        response = requests.request("get", url, headers=headers, data=payload)
        _logger.info("-------------------Return Response------------------------------------")
        _logger.info( pprint.pformat(response.json()))
        response = response.json()  

        """" 
                From Get  Invoice list, loop the disc to set unsetted pos purchase order

        """

        all_data = response 
        _logger.info("Invoice Lenght:%s",len(all_data))
     
        for loop in all_data:
           
            # ackNo = loop['AckNo']
            data1 = {
                "AckNo": "1190015-10" #ackNo
                }
                            # try:
            # if buyer.id == self.env.uid:
            res = requests.post(f"https://invoice-reg.api.qa.addissystems.et/getInvoice",   data=json.dumps(data1) ,headers=headers)
            order= res.json()

            _logger.info(pprint.pformat(order))

            search_order = self.env['pos.purchase'].search([('name','=',order['Invoice_Desc']['Invoice_no'])])
            _logger.info(pprint.pformat(search_order))

            if len(search_order) > 10:
                pass
            else:
                vals = []
                data = {
                    'name': order['Invoice_Desc']['Invoice_no'],
                    'seller_tin': order['Seller']['company_name'],
                    'payment_term':  order['Payment_info']['payment_term'],
                    'vendor': order['Buyer']['company_name'],
                    'payment_means': order['Payment_info']['payment_means'],
                    # 'lines':[{
                    #     'product_id' : order['Invoice_line']['sno'],
                    #     'qty': order['Invoice_line']['qty'], 
                    #     'product_uom_id': order['Invoice_line']['unit'],
                    #     'price_unit':order['Invoice_line']['price'], 
                    #     'price_subtotal_incl': 1000,
                    #     'price_subtotal': 570,
                    #         }]
                }
            
                            # 'journal_id': 

                # _logger.info(order['Invoice_line'])
                # line_items = []    
                # for line in order['Invoice_line']:
                #     vals = []
                #     vals['product_id'] = line['sno'],
                #     vals['qty']= line['qty'], 
                #     vals['product_uom_id'] = line['unit'],
                #     vals['price_unit']= line['price'], 
                #     vals['price_subtotal_incl']= 0,
                #     vals['price_subtotal']= 0,
                #     line_items.append(vals)

              
                # # line_items.append(vals)

        
                # data = {
                #     "lines": data2
                # }
                # data['lines'] = data2

                _logger.info("########### Data:%s",data)

                create_pos_purchase = self.env['pos.purchase'].create(data)
                
                # vals["pos_purchase"] = create_pos_purchase.id,
                # vals['product_id'] = int(order['Invoice_line']['sno']),
                # vals['qty'] = order['Invoice_line']['qty'], 
                # vals['product_uom_id'] = order['Invoice_line']['unit'],
                # vals['price_unit'] = order['Invoice_line']['price'], 
                # vals['price_subtotal_incl'] = 1000,
                # vals['price_subtotal'] =  570,
                
                # _logger.info("########### Data:%s",vals)

                product = self.env['product.product'].search([('name','=',order['Invoice_line']['barcode'])],limit=1)
                price_subtotal = float(order['Invoice_line']['price']) * float(order['Invoice_line']['qty'])
                price_subtotal_incl = float(order['Invoice_line']['price']) * 1.15
                amount_tax = float(order['Invoice_line']['price']) * 0.15
                create_pos_purchase.lines.sudo().create({
                        'pos_purchase' : create_pos_purchase.id,
                        'product_id' : product.id,
                        'qty': order['Invoice_line']['qty'], 
                        'product_uom_id': 6,
                        'price_unit':order['Invoice_line']['price'], 
                        'price_subtotal_incl': str(price_subtotal_incl),
                        'price_subtotal': str(price_subtotal),
                })

                data  = {
                    'amount_tax': str(amount_tax),
                    'amount_total': str(price_subtotal_incl),
                    'amount_paid': str(price_subtotal_incl),
                }
                create_pos_purchase.write(data)

                _logger.info("Succeddfully created:%s",create_pos_purchase)
        
            
            # except Exception as e:
            #     raise ValidationError(e)


        sn = 0
        # headers = {"Content-Type": "json", "Accept": "json", "Catch-Control": "no-cache"}
        # url = "http://localhost:10013/my_sale_details"
        # response = requests.get(url)
        #http = urllib3.PoolManager()
        # URL = 'https://jsonplaceholder.typicode.com'
        # root = '/todos/1'
        #datas = http.request('GET', URL + root)
        #datas = json.loads(datas.data.decode('utf-8'))  # parses the response to  a compatible form
        # json_file = {'invoice_desc': {'taxschema': 'VAT', 'InvType': 'INV', 'Invoice_no': 'Order 00008-004-0001',
        #                               'Inv_Dt': (2022, 9, 29, 16, 32, 47)},
        #              'Invoice_source_process': {'process': 'AR', 'SupType': 'B2B'},
        #              'seller': {'tin_no': '00099887', 'licence_number': False, 'company_name': 'My Company (San Francisco)'},
        #              'Buyer': {'tin_no': False, 'licence_number': 100.0, 'company_name': False},
        #              'Payment_info': {'payment_means': 'Cash', 'payer_account': '18988766', 'payment_term': 'Net within 30 days'},
        #              'Invoice_total': 4594.4, 'Vat_breakdown': 0.0, 'Invoice_allowance': '0', 'Invoice_charge': 0,
        #              'Invoice_line': [(0, 0, {'product_id': 1,
        #                                     'qty': 1.0, 'product_uom_id': 1,
        #                                     'price_unit': 39.4, 'price_subtotal_incl': 39.4,'price_subtotal': 39.4,})]}

        # #raise UserError(
        #         #_(json_file['Invoice_line'][0][2]['unit']))
        # context = self._context
        # current_uid = context.get('uid')
        # user = self.env['res.users'].browse(current_uid)
        # operating_unit = user.default_operating_unit_id.id
        # journal_id = self.env['account.journal'].search([('operating_unit_id', '=', operating_unit),('type', '=', 'purchase')])
        # for line in journal_id:
        #     journal_ids = line.id
        # pur_vals = {
        #     'name': json_file['invoice_desc']['Invoice_no'],
        #     'seller_tin': json_file['seller']['tin_no'],
        #     'vendor': json_file['seller']['company_name'],
        #     'payment_means': json_file['Payment_info']['payment_means'],
        #     'payment_term': json_file['Payment_info']['payment_term'],
        #     'amount_tax': json_file['Vat_breakdown'],
        #     'amount_total': json_file['Invoice_total'],
        #     'journal_id': journal_ids,
        #     'lines': json_file['Invoice_line'],
        # }
        # moves = self.env['pos.purchase'].create(pur_vals)

class PosPurchaseLine(models.Model):
    _name = "pos.purchase.line"

    pos_purchase = fields.Many2one('pos.purchase', string='Order Ref', ondelete='cascade', index=True)
    name = fields.Char(string='Line No', copy=False)
    notice = fields.Char(string='Discount Notice')
    product_id = fields.Many2one('product.product', string='Product',
                                 change_default=True)
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)
    price_subtotal = fields.Float(string='Subtotal w/o Tax', digits=0,
                                  readonly=True)
    price_subtotal_incl = fields.Float(string='Subtotal', digits=0,
                                       readonly=True, required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Product UoM', related='product_id.uom_id')
    tax_ids = fields.Many2many('account.tax', string='Taxes', readonly=True)