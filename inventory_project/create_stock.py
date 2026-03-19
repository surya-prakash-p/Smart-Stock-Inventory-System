import requests

url = "http://localhost:9000"

xml = """
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
    <TALLYMESSAGE xmlns:UDF="TallyUDF">
     <STOCKITEM NAME="Bike Oil" ACTION="Create">
      <NAME>Bike Oil</NAME>
      <PARENT>Primary</PARENT>
     </STOCKITEM>
    </TALLYMESSAGE>
   </REQUESTDATA>
  </IMPORTDATA>
 </BODY>
</ENVELOPE>
"""

response = requests.post(url, data=xml)

print(response.text)