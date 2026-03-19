import requests
from datetime import datetime

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Lachu Auto Traders"


# 🔥 COMMON FUNCTION
def send_to_tally(xml):
    try:
        response = requests.post(TALLY_URL, data=xml)
        print("Tally Response:", response.text)
        return response.text
    except Exception as e:
        print("Tally Connection Error:", e)
        return None


# 🔥 CREATE CUSTOMER
def create_customer(name):
    xml = f"""
<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Import Data</TALLYREQUEST>
 </HEADER>
 <BODY>
  <IMPORTDATA>
   <REQUESTDESC>
    <REPORTNAME>All Masters</REPORTNAME>
   </REQUESTDESC>
   <REQUESTDATA>
    <TALLYMESSAGE>
     <LEDGER ACTION="Create">
      <NAME>{name}</NAME>
      <PARENT>Sundry Debtors</PARENT>
     </LEDGER>
    </TALLYMESSAGE>
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
"""
    print(f"\nCreating Customer: {name}")
    send_to_tally(xml)


# 🔥 CREATE STOCK ITEM
def create_stock_item(name, qty=0):
    xml = f"""
<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Import Data</TALLYREQUEST>
 </HEADER>
 <BODY>
  <IMPORTDATA>
   <REQUESTDESC>
    <REPORTNAME>All Masters</REPORTNAME>
   </REQUESTDESC>
   <REQUESTDATA>
    <TALLYMESSAGE>
     <STOCKITEM ACTION="Create">
      <NAME>{name}</NAME>
      <BASEUNITS>Nos</BASEUNITS>
      <OPENINGBALANCE>{qty} Nos</OPENINGBALANCE>
     </STOCKITEM>
    </TALLYMESSAGE>
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
"""
    print(f"\nCreating Stock: {name}")
    send_to_tally(xml)

def create_sales_entry(product_name, qty, price, customer="Cash"):

    total = price * qty
    date = "20250402"   # 🔥 fixed test date

    xml = f"""
<ENVELOPE>

 <HEADER>
  <TALLYREQUEST>Import Data</TALLYREQUEST>
 </HEADER>

 <BODY>

  <DESC>
   <STATICVARIABLES>
    <SVCURRENTCOMPANY>Lachu Auto Traders</SVCURRENTCOMPANY>
   </STATICVARIABLES>
  </DESC>

  <DATA>

   <TALLYMESSAGE>

    <VOUCHER VCHTYPE="Sales" ACTION="Create">

     <DATE>{date}</DATE>
     <EFFECTIVEDATE>{date}</EFFECTIVEDATE>

     <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
     <PARTYLEDGERNAME>Cash</PARTYLEDGERNAME>

     <ALLINVENTORYENTRIES.LIST>
      <STOCKITEMNAME>{product_name}</STOCKITEMNAME>
      <RATE>{price}/Nos</RATE>
      <AMOUNT>{total}</AMOUNT>
      <ACTUALQTY>{qty} Nos</ACTUALQTY>
      <BILLEDQTY>{qty} Nos</BILLEDQTY>
     </ALLINVENTORYENTRIES.LIST>

     <LEDGERENTRIES.LIST>
      <LEDGERNAME>Cash</LEDGERNAME>
      <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
      <AMOUNT>-{total}</AMOUNT>
     </LEDGERENTRIES.LIST>

     <LEDGERENTRIES.LIST>
      <LEDGERNAME>Sales</LEDGERNAME>
      <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
      <AMOUNT>{total}</AMOUNT>
     </LEDGERENTRIES.LIST>

    </VOUCHER>

   </TALLYMESSAGE>

  </DATA>

 </BODY>

</ENVELOPE>
"""

    response = requests.post(TALLY_URL, data=xml)
    print("Sales Response:", response.text)


# 🔥 SYNC ALL PRODUCTS
def sync_all_products(products):
    for product in products:
        create_stock_item(product.name, product.quantity)


# 🔥 SYNC DELIVERED ORDERS
def sync_delivered_orders(orders):

    for order in orders:
        if order.status == "delivered":

            try:
                customer = (
                    order.user.username
                    if order.user else "Walk-in Customer"
                )

                print(f"\nProcessing Order: {order.product.name}")

                create_customer(customer)
                create_stock_item(order.product.name, order.product.quantity)

                price_per_item = order.price // order.quantity

                create_sales_entry(
                    order.product.name,
                    order.quantity,
                    price_per_item,
                    customer
                )

            except Exception as e:
                print("Sync Order Error:", e)