import frappe
from .enums import Material_Type

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
    stock_management.save(ignore_permissions=True)
    stock_management.submit()
    return stock_management

def check_stock_balance(entry_for, entry_item, warehouse, check_for_quantity=None):
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
    if exists and check_for_quantity==None:
        return True
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

def get_stock_balance(entry_for, entry_item, warehouse):
    exists = check_stock_balance(entry_for, entry_item, warehouse)
    if exists:
        quantity = frappe.get_value("Stock Balance", filters={
					'entry_for': entry_for,
					'entry_item': entry_item,
					'warehouse': warehouse,
					'docstatus': 1
				}, fieldname="quantity")
        return quantity
    else:
        return 0
        #frappe.throw(f"Stock Balance Not Available Warehouse: {warehouse} for Item: {entry_item}. Create Opening Stock Entry First.")

def update_blend_insigts(batch, blend, enabled=True, consumed_qty=None):
    found = False
    batch_doc = frappe.get_doc("Batch", batch)
    for blend_insight in batch_doc.blend_insights:
        if blend == blend_insight.blend:
            found = True
            blend_insight.enabled = enabled
            if consumed_qty:
                blend_insight.consumed_qty = consumed_qty
            break

    if not found:
        batch_doc.append("blend_insights", {
                    "blend": blend,  
                    "enabled": enabled
                })
    
    batch_doc.save(ignore_permissions=True)

def update_polymer_insigts(batch, doc):
    batch_doc = frappe.get_doc("Batch", batch)
    
    for doc_item in doc.polymers:
        found = False
        for polymer_insight in batch_doc.batch_polymer_insights: 
            if ((doc_item.polymer == polymer_insight.polymer) and (doc_item.quantity == polymer_insight.required_qty)):
                found = True
                polymer_insight.enabled = doc.enabled
                break

        if not found:
            batch_doc.append("batch_polymer_insights", {
                    "polymer": doc_item.polymer,
                    "required_qty": doc_item.quantity,  
                    "enabled": doc.enabled
                })
    
    batch_doc.save(ignore_permissions=True)

def delete_blend_insigts(batch, blend):
    batch_doc = frappe.get_doc("Batch", batch)
    for blend_insight in batch_doc.blend_insights:
        if blend == blend_insight.blend:
            batch_doc.blend_insights.remove(blend_insight)
            break
    batch_doc.save(ignore_permissions=True)

def delete_polymer_insigts(batch, doc):
    batch_doc = frappe.get_doc("Batch", batch)
    for doc_item in doc.polymers:
        for polymer_insight in batch_doc.batch_polymer_insights:
            if doc_item.polymer == polymer_insight.polymer and doc_item.quantity == polymer_insight.required_qty:
                #frappe.msgprint(f" doc_item {doc_item.polymer}, polymer_insight {polymer_insight.polymer}, {doc_item.quantity}, {polymer_insight.required_qty}")
                batch_doc.batch_polymer_insights.remove(polymer_insight)
    
    batch_doc.save(ignore_permissions=True)


def update_batch_insights_from_material_transfer(doc, method=None):
    batch_doc = frappe.get_doc("Batch", doc.batch)
    for material in doc.material_transfer:
         if (doc.type == "Material Issue" and method == "on_submit") or (doc.type == "Material Return" and method == "on_cancel"):
            if material.material_type == "Bag":
                for bag_row in batch_doc.batch_bag_insights:
                     if bag_row.bag == material.material:
                         bag_row.issued_qty += material.quantity
            elif material.material_type == "Pallet":
                if batch_doc.pallet_code == material.material:
                    batch_doc.pallet_issued_qty += material.quantity
            elif material.material_type == "Polymer":
                for polymer_row in batch_doc.batch_polymer_insights:
                     if polymer_row.polymer == material.material:
                         polymer_row.issued_qty += material.quantity
         elif (doc.type == "Material Return" and method == "on_submit") or (doc.type == "Material Issue" and method == "on_cancel"):
             if material.material_type == "Bag":
                for bag_row in batch_doc.batch_bag_insights:
                     if bag_row.bag == material.material:
                         bag_row.issued_qty -= material.quantity
             elif material.material_type == "Pallet":
                if batch_doc.pallet_code == material.material:
                    batch_doc.pallet_issued_qty -= material.quantity

             elif material.material_type == "Polymer":
                for polymer_row in batch_doc.batch_polymer_insights:
                     if polymer_row.polymer == material.material:
                         polymer_row.issued_qty -= material.quantity
    
    batch_doc.save(ignore_permissions=True)

def stock_management_update_batch_insights(doc, method=None):
    if doc.stock_entry_for == "Blend":
        blend_doc = frappe.get_doc("Blend", doc.stock_entry_item)
        blend_doc.blend_stock = get_stock_balance("Blend", doc.stock_entry_item, "Blend Warehouse")
        blend_doc.save(ignore_permissions=True)
		
# def assign_blend_batch_insight(doc, method=None):
#     blend_doc = frappe.get_doc("Blend", doc.blend)
#     batch_doc = frappe.get_doc("Batch", doc.batch)
#     for polymer_item in blend_doc.select_polymer_section:
#         found = False
#         for polymer_insight in batch_doc.batch_polymer_insights:
#                 if polymer_insight.polymer == polymer_item.polymer:
#                     found = True
#                     polymer_insight.enabled = doc.enabled
#         if not found:
#             batch_doc.append("batch_polymer_insights", {
#                     "polymer": polymer_item.polymer,  
#                     "enabled": doc.enabled
#                 })

def generate_machine_log(machine, log_type, hours, ref_doc_name, ref_doc_link, batch=None, quantity=None, downtime_reason=None):
    machine_log = frappe.new_doc("Machine Log")
    machine_log.machine = machine
    machine_log.log_type = log_type
    machine_log.hours = hours
    machine_log.reference_doc_name = ref_doc_name
    machine_log.reference_doc_link = ref_doc_link
    if batch:
        machine_log.batch = batch
    if quantity:
        machine_log.quantity = quantity
    if downtime_reason:
        machine_log.downtime_reason = downtime_reason
    
    machine_log.save(ignore_permissions=True)
    machine_log.submit()

    return machine_log

def validate_issue(batch, material_type, material, qty_to_check):
    batch_doc = frappe.get_doc("Batch", batch)
    if material_type == Material_Type.BAG.value:
        for bag_row in batch_doc.batch_bag_insights:
            if bag_row.bag == material and bag_row.issued_qty < qty_to_check:
                return False
    elif material_type == Material_Type.POLYMER.value:
        for polymer_row in batch_doc.batch_polymer_insights:
            if polymer_row.polymer == material and polymer_row.issued_qty < qty_to_check:
                return False
    elif material_type == Material_Type.PALLET.value:
        if batch_doc.pallet_issued_qty < qty_to_check:
            return False
    return True

# @frappe.whitelist()
# def cancel_linked_prod_docs(prod):
#     prod_doc = frappe.get_doc("Production", prod)
#     stock_list = frappe.get_list("Stock Management", filters={"created_from_doc": "Production", "doc_link": prod_doc})
#     frappe.throw(f"{stock_list}")
    
