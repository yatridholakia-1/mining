# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
from ..enums import Stock   
from frappe.utils import nowdate


class StockManagement(Document):

    def on_submit(self):
         if self.stock_entry_type == Stock.STOCK_IN.value:
            manageStock(
                self.stock_entry_for,
                self.stock_entry_item,
                self.target_warehouse,
                self.quantity,
            )
         elif self.stock_entry_type == Stock.STOCK_OUT.value:
          manageStock(
                self.stock_entry_for,
                self.stock_entry_item,
                self.source_warehouse,
                -self.quantity,
            )
         elif self.stock_entry_type == Stock.STOCK_TRANSFER.value:
             transferStock(
                self.stock_entry_for,
                self.stock_entry_item,
                self.source_warehouse,
                self.target_warehouse,
                self.quantity,
             )

    def on_cancel(self):
         #Restrict cancellation of linked documents
        # if self.doc_link:
        #     frappe.throw("Cannot Cancel Linked Stock Entries!")
            
        if self.stock_entry_type == Stock.STOCK_IN.value:
            manageStock(
                self.stock_entry_for,
                self.stock_entry_item,
                self.target_warehouse,
                -self.quantity,
        )
        elif self.stock_entry_type == Stock.STOCK_OUT.value:
            manageStock(
                self.stock_entry_for,
                self.stock_entry_item,
                self.source_warehouse,
                self.quantity,
            )
        elif self.stock_entry_type == Stock.STOCK_TRANSFER.value:
            reverseTransferStock(
            self.stock_entry_for,
            self.stock_entry_item,
            self.source_warehouse,
            self.target_warehouse,
            self.quantity,
            )
            
    def after_insert(self):
        self.date = nowdate()
        self.save()

def manageStock(entry_for: str, entry_item: str, warehouse: str, quantity: int):
	update_stock_balance(entry_for, entry_item, warehouse, quantity)

def transferStock(entry_for: str, entry_item: str, s_warehouse: str, t_warehouse: str, quantity: int):
    update_stock_balance(entry_for, entry_item, s_warehouse, -quantity)
    update_stock_balance(entry_for, entry_item, t_warehouse, quantity)

def reverseTransferStock(entry_for: str, entry_item: str, s_warehouse: str, t_warehouse: str, quantity: int):
    update_stock_balance(entry_for, entry_item, t_warehouse, -quantity)
    update_stock_balance(entry_for, entry_item, s_warehouse, quantity)


def create_stock_balance(entry_for: str, entry_item: str, warehouse: str, quantity: int):
    
    if quantity < 0:
        frappe.throw(f"Creating Stock Balance: Quantity Cannot Be Less Than 0 for item {entry_item}!")
    

    else:
     stock_balance = frappe.new_doc("Stock Balance")
     stock_balance.entry_for = entry_for
     stock_balance.entry_item = entry_item
     stock_balance.warehouse = warehouse
     stock_balance.quantity = quantity
     stock_balance.rol = frappe.db.get_value("Material", entry_item, "rol_quantity") if entry_for == "Material" else 0
     stock_balance.save(ignore_permissions=True)
     stock_balance.submit()


def update_stock_balance(entry_for: str, entry_item: str, warehouse: str, quantity: int):
    #Check if entry-for_entry-item_warehouse combination exists
    exists = frappe.db.exists(
            'Stock Balance',
            {
                'entry_for': entry_for,
                'entry_item': entry_item,
                'warehouse': warehouse,
                'docstatus': 1,    
            })
    #if it exists fetch and update
    if exists:
       stock_balance = frappe.get_doc("Stock Balance", {
           'entry_for': entry_for,
                'entry_item': entry_item,
                'warehouse': warehouse,
                'docstatus': 1,    
	   })
       new_quantity = quantity + stock_balance.quantity
       
       if new_quantity < 0:
           frappe.throw(f"Stock-out quantity for {entry_item} exceeding current stock available.", title="Stock Unavailable")
           new_quantity = 0
           
       stock_balance.quantity = new_quantity
       stock_balance.last_updated_on = now()
       stock_balance.save(ignore_permissions=True)
       
    #else create new entry   
    else:
        create_stock_balance(entry_for, entry_item, warehouse, quantity)


