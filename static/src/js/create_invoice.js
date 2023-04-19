odoo.define('pos_customization.PaymentScreenButton', function(require) {
'use strict';
   const { Gui } = require('point_of_sale.Gui');
   const PosComponent = require('point_of_sale.PosComponent');
   const { posbus } = require('point_of_sale.utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require('web.custom_hooks');
   const Registries = require('point_of_sale.Registries');
   const ReceiptScreen = require('point_of_sale.ReceiptScreen');
   const ajax = require('web.ajax');
   const rpc = require('web.rpc');
//   const qweb = core.qweb;
const CustomButtonPaymentScreen = (ReceiptScreen) =>

class extends ReceiptScreen {
    constructor() {
           super(...arguments);
        }
    IsCustomButton() {
               // click_invoice
            const order = this.currentOrder;
            var data = {
               "order": order.name,
               "date": this.getFormattedDate(this.currentOrder.formatted_validation_date),
               "buyer_address": this.currentOrder.attributes.client.address
            }
            console.log("data:",data)
            this.getPostData(data);
    
           }
           
           

           async getPostData(data) {
               const tController = new AbortController()
               const timeoutId = setTimeout(() => tController.abort(), 20000)
               try{
                
                  var res = await  this.rpc({
                     model: 'pos.order',
                     method: 'postInvoiceInformation',
                     args: [[],data]
                     });
      
                     console.log("Return:",res)
                     console.log(res.success)
                     if (res.success === true){
                           alert("E-Invoice Record Successfully")
                          
                     }
                     if (res.success != true){
                        alert(res.message)
                  }  
               }catch(err) {
                  console.log(err)
                  alert(err)
            }finally {
                  clearTimeout(timeoutId);
            }
         }



           getLineItems(orderlines){
            console.log("orderlines",orderlines)
            let lineItems = [];
            console.log("length:",orderlines.models.length)
            for(let i =0; i<orderlines.models.length; i++){
               console.log("loop",i)
               var data = {
                  "sno":  i+1 , 
                  "hsncode": 8987 , 
                  "barcode": "878765554545" , 
                  "qty":  orderlines.models[i].quantity.toFixed(2),
                  "unit": "Pc", 
                  "price": orderlines.models[i].price, 
                  "tax": 15, 
                  "Line_allowance_code":  "ewr123" , 
                  "Line_allowance_reason": "qwe1232" , 
                  "Line_allowance_amount": "qazxsw12345" , 
                  "Line_charge_code": "qew12345" , 
                  "Line_charge_reason": "qazxsw12345" , 
                  "Line_charge_amount": "qazxsw12345" , 
                  "total_price":  orderlines.models[i].price, 
               }
               
               lineItems.push(data)
            }
            return [lineItems]
           }
           getFormattedDate(date){//02/11/2022 15:21:42-----------2021-11-09 12:58:10 
            var d = String(date).split(' ')
            var dt = String(d[0]).split('/')
            return `${dt[2]}-${dt[0]}-${dt[1]}`
            }

         getPaymentData(paymentlines){
               let Payment_info = [];
               console.log("length:",paymentlines.length)
               for(let i =0; i<paymentlines.length; i++){
                  console.log("loop",i)
                  var data = {
                     "payment_means": paymentlines.models[i].name,
                     "payer_account": "18988766",
                     "payment_term": "Net within 30 days"
                  }
                  
                  Payment_info.push(data)
               }
               return [Payment_info]
              }

           getDatas(orderlines){
            console.log("Get Data")
            let invoice_ref = [];
            let Invoice_Desc = [];
            let Invoice_source_process = [];
            let Seller = [];
            let Buyer = [];
            let payee = [];
            let lineItems = [];
            
            
               var invoiceRef = {
                  "Buy_ref_no": this.currentOrder.name,
                  "Project_ref_no": 758687, 
                  "cont_ref_no": 8945858, 
                  "PO_ref_no":this.currentOrder.name, 
                  "Selles_order_ref_no":564535, 
                  "Rec_advice_ref_no":8768597, 
                  "Disp_advce_ref_no":5635654, 
                  "Tander_ref_no":7454379, 
                  "Invo_obj_ref_no":758958598 
                  }
                  invoice_ref.push(invoiceRef)

               var InvoiceDesc = { 
                  "taxschema": "VAT", 
                  "InvType": "B2B", 
                  "Invoice_no": this.currentOrder.uid, 
                  "Inv_date": this.getFormattedDate(this.currentOrder.formatted_validation_date)
               
                  }
                  Invoice_Desc.push(InvoiceDesc)

               var InvoiceSourceProcess =   {
                  "process": "AR", 
                  "subpype": "B2B", 
                  "process_reference_no": 1000098799 
                  }
                  Invoice_source_process.push(InvoiceSourceProcess)
                
               var seller = { 
                  "tin_no": this.currentOrder.pos.company.vat,
                  "licence_no": 100, 
                  "vat_reg_no":  this.currentOrder.pos.company.company_registry,                  
                  "vat_reg_Dt": this.getFormattedDate(this.currentOrder.formatted_validation_date), 
                  "company_name": this.currentOrder.pos.company.name  
                  }
                  Seller.push(seller)  

               var buyer = { 
                  "tin_no": this.currentOrder.attributes.client.vat, 
                  "vat_reg_no":  100 ,
                  "address":  this.currentOrder.attributes.client.address , 
                  "location": "Company XYZ" , 
                  "phone_no": this.currentOrder.attributes.client.phone, 
                  "email":  this.currentOrder.attributes.client.email , 
                  "buyer_name": this.currentOrder.attributes.client.name  
                  }
                  Buyer.push(buyer)

               var payees = {
                  "id": 67578, 
                  "name": this.currentOrder.attributes.client.name  , 
                  "regstration_number":109090903, 
                  "bank": 8945858, 
                  "bank_account":8945858, 
                  "legal_registration":8945858 
                  }
                  payee.push(payees)


               
                  
               


            return [invoice_ref, Invoice_Desc,Invoice_source_process,Seller, Buyer, payee,lineItems];
        }


           async getData(tin=undefined) {
            
            try{
                let validationErrorMessage = '';
                let isError = false;
                
                console.log("BEFORE#################")
                console.log(this.currentOrder)
                const {invoice_ref,Invoice_Desc,Invoice_source_process, Seller, Buyer,payee} =  this.getDatas(this.currentOrder.orderlines);
                const {lineItems} =  this.getLineItems(this.currentOrder.orderlines);
                const {Payment_info} = this.getPaymentData(this.currentOrder.paymentlines)

                const data = {
                  "invoice_ref": invoice_ref,
                  "Invoice_Desc": Invoice_Desc,
                  "Invoice_source_process": Invoice_source_process,
                  "Seller": Seller,
                  "Buyer": Buyer,
                  "payee": payee,
                  "Delivery_info": 	"Addis Ababa, Ethiopia",
                  "Payment_info": Payment_info,
                  "Invoice_total":	344,
                  "Vat_breakdown":	15,
                  "Invoice_allowance":	0,
                  "Invoice_charge": 0,
                  "LineItem": lineItems
                };
                console.log("PostData:",data)
                
             
                if(!isError){
                    console.log("THIS")
                    console.log(this)
                    console.log("POST Json")
                    console.log(data)

                  //   const order = this.currentOrder;
                  //   rpc.query({
                  //                 model: 'pos.order',
                  //                 method: 'postInvoiceInformation',
                  //                 args: [[], order.name ]
                  //               }).then(function(result){
                  //                       console.log("click", result)
                  //                       alert('response'+result)
                  //                       });
                    await this.sendInvoiceInformation(data);
                        
                     }
                    else{
                        throw new Error("Check your connection");
                    }
              
              
            }
            catch(err) {
                console.log(err)
                this.is_clicked = false;
                this.is_clicked_count = 0;
                alert("Error occured while printing, please try again or contact your manager!")
            }finally {
                this.is_clicked = false;
                this.is_clicked_count = 0;
            }
        }


        async sendInvoiceInformation(data){
         const tController = new AbortController()
         const timeoutId = setTimeout(() => tController.abort(), 30000)
         try{
             console.log("Sending....")
             console.log(data)
          

             const response = await fetch("https://invoice-reg.api.qa.addissystems.et/Invoice-Registration", {
                 method:'POST',
                 body:JSON.stringify({
                     "data":data
                 }),
                 headers:{
                     'Accept': 'application/json',
                     'Content-Type': 'application/json',
                 },
                 signal: tController.signal
             })
             let res = await response.json();
             console.log("#######RESPONSE")
             console.log(res);

             
            
             
             
         }catch(err) {
             console.log(err)
             this.is_clicked = false;
             this.is_clicked_count = 0;
             alert(err)
         }finally {
             this.is_clicked = false;
             this.is_clicked_count = 0;
             console.log("FINALLLLYY1")
             clearTimeout(timeoutId);
         }
     }
    };
   Registries.Component.extend(ReceiptScreen, CustomButtonPaymentScreen);
   return CustomButtonPaymentScreen;
});