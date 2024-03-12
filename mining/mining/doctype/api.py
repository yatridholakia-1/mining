import frappe

def create_stock_entry(**kwargs):
    stock_management = frappe.new_doc("Stock Management")
    stock_management.stock_entry_for = kwargs.get('stock_entry_for')
    stock_management.stock_entry_item = kwargs.get('stock_entry_item')
    stock_management.stock_entry_type = kwargs.get('stock_entry_type')
    stock_management.stock_entry_purpose = kwargs.get('stock_entry_purpose')                       
    stock_management.source_warehouse = kwargs.get('source_warehouse') or None
    stock_management.target_warehouse = kwargs.get('target_warehouse') or None
    stock_management.quantity = kwargs.get('quantity')
    stock_management.created_from_doc = kwargs.get('created_from_doc')
    stock_management.doc_link = kwargs.get('doc_link')
    stock_management.save()
    stock_management.submit()
    return stock_management.name

def check_stock_balance(entry_for, entry_item, warehouse, check_for_quantity):
    exists = frappe.db.exists(
				'Stock Balance',
				{
					'entry_for': entry_for,
					'entry_item': entry_item,
					'warehouse': warehouse,
					'docstatus': 1,    
				},
			)
    
    if not exists:
        return False
    else:
        actual_quantity = frappe.get_value("Stock Balance", filters={
					'entry_for': entry_for,
					'entry_item': entry_item,
					'warehouse': warehouse,
					'docstatus': 1
				}, fieldname="quantity")
        if actual_quantity < check_for_quantity:
            return False
    
    return True
				
			