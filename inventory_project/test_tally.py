import sys
sys.path.append('c:\\Users\\Surya Prakash\\OneDrive\\Desktop\\smart_inventory management\\smart_inventory\\inventory_project')
from inventory.tally_integration import create_sales_entry

print("Testing Sales Entry to Tally to see why stock fails to update...")
# We sell 1 Brake lever for 100 Rs
result = create_sales_entry("Brake lever", 1, 100.0)
print("Tally Final Response:", result)
