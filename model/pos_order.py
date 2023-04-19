from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import string
import pickle
import pprint
import json
# from jmespath import search
import psycopg2
import pytz
import re
import requests
import logging


from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64
_logger = logging.getLogger(__name__)



class PosOrder(models.Model):
    _inherit = "pos.order"

    is_eInvoiced = fields.Boolean(default="False")
    invoice_id = fields.Char()
    AckNo = fields.Char()
    AckDt = fields.Char()
    Created_Date = fields.Char()
    IRN = fields.Char()
    Inv_Status = fields.Char()
    Signed_invoice = fields.Char()
    Signed_QRCode = fields.Char()
    Created_by = fields.Char()
    Created_Date = fields.Char()
    seller_id = fields.Char()
    buyer_id = fields.Char()
    is_send = fields.Boolean(default="False")
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'), ('paid', 'Paid'),
        ('e_invoic_send', 'E-Invoiced'),
         ('done', 'Posted'),('invoiced', 'Invoiced')],
        'Status', readonly=True, copy=False, default='draft')



    def postInvoiceInformation(self, data):
        sn = 0
        _logger.info("data:%s",data)
        order_i = str(data['order'])
        orders = self.env['pos.order'].search([('pos_reference', '=', order_i)])
        user = self.env.user
        for order1 in orders:
            data = {

                "Invoice_Reference": {
                    "Buy_ref_no": order_i,
                    "Project_ref_no": "000000", 
                    "cont_ref_no":" 000000", 
                    "PO_ref_no": order_i, 
                    "Sellers_order_ref_no":order_i, 
                    "Rec_advice_ref_no":"0000000", 
                    "Disp_advice_ref_no":"00000", 
                    "Tender_ref_no":"7454379", 
                    "Invo_obj_ref_no":order_i

                },
                "Invoice_Desc": {
                
                    "taxschema": "VAT",
                    "InvType": "INV",
                    "Invoice_no": order_i,
                    "Invoice_ref": "1000098799",
                    "Inv_Dt": data['date'],
                    "payment_due_Dt": data['date'],

                },
                "Invoice_source_process": {

                    "process": "AR", 
                    "SupType": "B2B", 
                    "proccess_reference_no": order_i 
                },
                "Seller": {
                
                    "tin_no": user.company_id.vat,
                    "license_number": user.company_id.company_registry,
                    "vat_reg_no": user.company_id.company_registry,
                    "vat_reg_Dt": data['date'],
                    "company_name": user.company_id.name,

                },
                "Buyer": {
                    "tin_no": order1.partner_id.vat,
                    "vat_reg_no":  '100' ,
                    "address": data['buyer_address'],#order1.partner_id.address,
                    "location": order1.partner_id.name , 
                    "phone_no": order1.partner_id.phone,
                    "email": order1.partner_id.email,
                    "company_name": order1.partner_id.name,

                },
                "Payee": {
                
                    "id": "123123",
                    "name": order_i, 
                    "registration_number":order_i, 
                    "bank": "8945858", 
                    "bank_account":"8945858", 
                    "legal_registration":"8945858" 
                },
                "Delivery_info": {

                    "Delivery_note_number": "0000000",
                    "delivery_date": data['date'],
                    "delivery_location": order1.partner_id.name,
                    "delivery_address": data['buyer_address'],
                },
                "Payment_info": {
                    "payment_means": order1.payment_ids[0].payment_method_id.name,
                    "payer_account": "18988766",
                    "payment_term": "Net within 30 days"

                },
                "Invoice_total": str(order1.amount_total),
                "Vat_breakdown": {
                    "Vat_category_code": "1102",
                    "Vat_reason_code": "abc2354",
                    "Vat_reason_text": "ewrt234",
                    "Vat_breakdown_amount": str(order1.amount_tax),
                },
                "Invoice_allowance": "0",
                "Invoice_charge": "0",
                "Invoice_line": {
                    "sno": "1",
                    "hsncode": "100",
                    "barcode": str(order1.lines[0].product_id.name),
                    "qty": str(order1.lines[0].qty),
                    "unit": 'pc',
                    "period": "01-01-2015",
                    "price": str(order1.lines[0].price_unit),
                    "tax": str(order1.lines[0].tax_ids_after_fiscal_position.id),
                    "Line_allowance_code": "ewr123",
                    "Line_allowance_reason": "qawsed1234",
                    "Line_allowanece_amount": "1231231",
                    "Line_charge_code": "qwe1234",
                    "Line_charge_reason": "qazxsw12345",
                    "Line_charge_amount": "2121",
                    "total_price": str(order1.lines[0].price_unit)
                }
            }


            # for payment in order1.payment_ids:
            #  data['Payment_info'].append({
            #          "payment_means": payment.payment_method_id.name,
            #          "payer_account": "000000",
            #          "payment_term": "Net within 30 days"
            #                     })
            #  for line in order1.lines:
            #      sn =sn +1
            #      data['Invoice_line'].append({

            #             'Line_allowance_amount"': '0',
            #             'Line_allowance_code': '000',
                            # "Line_allowanece_amount": "1231231",   
            #             'Line_charge_amount"': '0',
            #             'Line_charge_code"': '0000',
            #             'Line_charge_reason"': 'No reason',
            #             'barcode': '3434343',
            #             'hsncode': '100',
            #             'period': '01-01-2015',
            #             'price': line.price_unit,
            #             'qty': line.qty,
            #             'sno': sn,
            #             'tax': line.tax_ids_after_fiscal_position.id,
            #             'total_price"':line.price_unit,
            #             'unit': 'pc'
            #             })

            # data['Invoice_line'] = {}
            _logger.info("Data2:%s",pprint.pformat(data))
            payload = json.dumps(data)
            url = "https://invoice-reg.api.qa.addissystems.et/Invoice-Registration"
            headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                    }

            response = requests.request("POST", url, headers=headers, data=payload)
            _logger.info("-------------------Return Response------------------------------------")
            _logger.info( pprint.pformat(response.json()))
            response = response.json()  
            
            """" 
                UPDATING THE INVOICE RETURN VALUE TO POS ORDER
            """
            try:
            # if response.status_code >= 200 and response.status_code <= 300:
                orders.write({
                    'is_eInvoiced': True,
                    'Inv_Status' : response['Inv_Status'],
                    'AckNo' : response['AckNo'],
                    'AckDt' : response['AckDt'],
                    'Created_Date' : response['Created_Date'],
                    'IRN' : response['IRN'],
                    'Signed_invoice' : response['Signed_invoice'],
                    'Signed_QRCode' : response['Signed_QRCode'],
                    'Created_by' : response['Created_by']
                    
                })
                # else :
                #     raise ValidationError("E-Invoice not Recorded, Please check the keys or Json body" + str(response.status_code))
                

                # if response['success'] == True:
                #     return {
                #         'success': True,
                #         'data' : {
                #         'AckNo': response['AckNo'],
                #         'Created_by': response['Created_by'],
                #         'IRN': response['IRN'],
                #         '_id': response['_id']
                #         }
                #     }
                # else:
                #     return {
                #         'success': False
                #     }
                return {
                        'success': True,
                        'data' : {
                        'AckNo': response['AckNo'],
                        'Created_by': response['Created_by'],
                        'IRN': response['IRN'],
                        }
                    }
            except Exception as e:
                return {
                    'success': False,
                    'message': response['message']
                }


   
    def send_invoice(self):
        _logger.info("########## Invoice Send############")

        invoice = self.env['pos.order'].search([('id','in',self.ids),('is_send','=','False')],limit=1)
        _logger.info("Invoiced:%s",invoice)

        post = {
            "AckNo": f"{invoice.AckNo}",
            "IRN": f"{invoice.IRN}",
            "seller_id": f"{self.env.user.company_id.name}",
            "buyer_id": f"{invoice.partner_id.name}",
            "Signed_invoice": f"{invoice.Signed_invoice}",
            "Signed_QRcode": f"{invoice.Signed_QRCode}",
            "Created_by": f"{invoice.Created_by}",
            "Created_Date": "1/1/15"
            }
        _logger.info("data:%s",pprint.pformat(post))     
        payload = json.dumps(post)
        url = "https://invoice-seller.api.qa.addissystems.et/Invoice-Seller"
        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'

                }
        response = requests.request("POST", url, headers=headers, data=payload)
        _logger.info("-------------------Return Response------------------------------------")
        _logger.info( pprint.pformat(response.json()))
        response = response.json()  
        """" 
        UPDATING THE INVOICE, Via RETURN VALUE
        
        """
        
        try:

          
            # if response['success'] == True:
            invoice.write({
                        'is_send': True,
                        'Signed_invoice':response['Signed_invoice'],
                        'state': "e_invoic_send"
                    })
            # else:
            #     raise ValidationError("Request not successful,Please check the keys or Json body")

            # response = response.json() 
            # _logger.info("status:%s",response.status_code)
            # if response.status_code >= 200 and response.status_code <= 300:
            #     invoice.write({
            #                 'is_send': True
            #             })
            # else :
            #     raise ValidationError("Request not successful,Please check the keys or Json body" + str(response.status_code))
        
        
        except Exception as e:
            raise ValidationError(response['message'])

            return {
                    'success': False,
                    'message': response['message']
                }


           
                       
