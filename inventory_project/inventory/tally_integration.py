import requests
from datetime import datetime
import xml.etree.ElementTree as ET

import os

# ✅ GRAB FROM ENV (For Render + Ngrok), FALLBACK TO LOCALHOST
TALLY_URL = os.environ.get("TALLY_URL", "https://interlinear-racquel-overdaintily.ngrok-free.dev")

COMPANY_NAME = "Lachu Auto Traders"

HEADERS = {
    "Content-Type": "application/xml",
    "ngrok-skip-browser-warning": "69420"
}

# =========================
# 🔥 COMMON SEND FUNCTION
# =========================
def send_to_tally(xml):
    try:
        response = requests.post(
            TALLY_URL,
            data=xml.encode("utf-8"),
            headers=HEADERS,
            timeout=10
        )

        print("\nTally Response:\n", response.text)
        return response.text

    except Exception as e:
        print("Tally Connection Error:", e)
        return None

# =========================
# 🔥 CREATE CUSTOMER
# =========================
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
    <STATICVARIABLES>
     <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
    </STATICVARIABLES>
   </REQUESTDESC>
   <REQUESTDATA>
    <TALLYMESSAGE xmlns:UDF="TallyUDF">
     <LEDGER NAME="{name}" ACTION="Create">
      <NAME>{name}</NAME>
      <PARENT>Sundry Debtors</PARENT>
     </LEDGER>
    </TALLYMESSAGE>
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
"""
    return send_to_tally(xml)


# =========================
# 🔥 CREATE STOCK ITEM
# =========================
def create_stock_item(name):
    xml = f"""
<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Import Data</TALLYREQUEST>
 </HEADER>
 <BODY>
  <IMPORTDATA>
   <REQUESTDESC>
    <REPORTNAME>All Masters</REPORTNAME>
    <STATICVARIABLES>
     <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
    </STATICVARIABLES>
   </REQUESTDESC>
   <REQUESTDATA>
    <TALLYMESSAGE xmlns:UDF="TallyUDF">
     <STOCKITEM NAME="{name}" ACTION="Create">
      <NAME>{name}</NAME>
      <PARENT>Primary</PARENT>
      <BASEUNITS>Nos</BASEUNITS>
     </STOCKITEM>
    </TALLYMESSAGE>
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
"""
    return send_to_tally(xml)


# =========================
# 🔥 CREATE SALES ENTRY (STOCK WILL REDUCE)
# =========================
def create_sales_entry(product_name, qty, price, customer="Cash"):
    total = qty * price
    # Tally Educational Mode only accepts 1st, 2nd or 31st!
    # Hardcoding to '20260301' (March 1, 2026) so Tally doesn't reject it.
    date = "20260301"

    xml = f"""
<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Import Data</TALLYREQUEST>
 </HEADER>
 <BODY>
  <IMPORTDATA>
   <REQUESTDESC>
    <REPORTNAME>Vouchers</REPORTNAME>
    <STATICVARIABLES>
     <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
    </STATICVARIABLES>
   </REQUESTDESC>
   <REQUESTDATA>
    <TALLYMESSAGE xmlns:UDF="TallyUDF">
     <VOUCHER VCHTYPE="Sales" ACTION="Create">

      <DATE>{date}</DATE>
      <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
      <PARTYLEDGERNAME>{customer}</PARTYLEDGERNAME>
      <PERSISTEDVIEW>Invoice Voucher View</PERSISTEDVIEW>
      <ISINVOICE>Yes</ISINVOICE>

      <ALLLEDGERENTRIES.LIST>
       <LEDGERNAME>{customer}</LEDGERNAME>
       <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
       <AMOUNT>-{total}</AMOUNT>
      </ALLLEDGERENTRIES.LIST>

      <ALLLEDGERENTRIES.LIST>
       <LEDGERNAME>Sales</LEDGERNAME>
       <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
       <AMOUNT>{total}</AMOUNT>

       <ALLINVENTORYENTRIES.LIST>
        <STOCKITEMNAME>{product_name}</STOCKITEMNAME>
        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
        <RATE>{price}/Nos</RATE>
        <ACTUALQTY>{qty} Nos</ACTUALQTY>
        <BILLEDQTY>{qty} Nos</BILLEDQTY>
        <AMOUNT>{total}</AMOUNT>
       </ALLINVENTORYENTRIES.LIST>
      </ALLLEDGERENTRIES.LIST>

     </VOUCHER>
    </TALLYMESSAGE>
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
"""
    return send_to_tally(xml)


# =========================
# 🔥 FETCH STOCK SUMMARY
# =========================
def get_stock_summary():
    xml = f"""
<ENVELOPE>
 <HEADER>
  <TALLYREQUEST>Export Data</TALLYREQUEST>
 </HEADER>

 <BODY>
  <DESC>
   <STATICVARIABLES>
    <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
   </STATICVARIABLES>
  </DESC>

  <EXPORTDATA>
   <REQUESTDESC>
    <REPORTNAME>Stock Summary</REPORTNAME>
   </REQUESTDESC>
  </EXPORTDATA>

 </BODY>
</ENVELOPE>
"""
    return send_to_tally(xml)


# =========================
# 🔍 PARSE STOCK
# =========================
def parse_stock_summary(xml_data):
    root = ET.fromstring(xml_data)
    items = []

    for item in root.findall(".//STOCKITEM"):
        items.append({
            "name": item.findtext("NAME"),
            "closing_balance": item.findtext("CLOSINGBALANCE"),
        })

    return items