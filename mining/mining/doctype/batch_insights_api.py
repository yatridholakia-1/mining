import frappe
from .enums import Material_Type, Batch_Insight_Headers, Warehouse, Stock, Stock_Purpose, Machine_Log_Type, Batch_State, BSB
from .api import check_stock_balance, create_stock_entry, generate_machine_log
from frappe.utils import now_datetime


def update_batch_insights(batch, material_type, header_name, quantity, material_code=None):
    """
    API for updating batch insights.

    Args:
        batch (str): Batch document name.
        material_type (str): Type of material (e.g., Bag, Polymer, Blend, Pallet).
        material_code (str): Code identifying the specific material.
        header_name (str): Name of the header (e.g., Issued, Consumed, Damaged, Remaining).
        quantity (float): Quantity to be updated.

    Returns:
        str: Confirmation message.
    """
    batch_doc = frappe.get_doc("Batch", batch)

    if material_type == Material_Type.BAG.value:
        update_bag_insights(batch_doc, material_code, header_name, quantity)
    elif material_type == Material_Type.POLYMER.value:
        update_polymer_insights(batch_doc, material_code, header_name, quantity)
    elif material_type == Material_Type.BLEND.value:
        update_blend_insights(batch_doc, header_name, quantity)
    elif material_type == Material_Type.PALLET.value:
        update_pallet_insights(batch_doc, header_name, quantity)

    batch_doc.save(ignore_permissions=True)

    return "Batch insights updated successfully."

def update_bag_insights(batch_doc, material_code, header_name, quantity):
    """Update batch insights for bags."""
    for bag_row in batch_doc.batch_bag_insights:
        if bag_row.bag == material_code:
            if header_name == Batch_Insight_Headers.ISSUED.value:
                bag_row.issued_qty += quantity
            elif header_name == Batch_Insight_Headers.CONSUMED.value:
                if bag_row.issued_qty < quantity:
                    frappe.throw(f"Not enough quantity of material: {bag_row.bag} is issued for consumption!")
                bag_row.consumed_qty += quantity
            elif header_name == Batch_Insight_Headers.DAMAGED.value:
                bag_row.damaged_qty += quantity
            elif header_name == Batch_Insight_Headers.REMAINING.value:
                bag_row.remaining_qty += quantity

def update_polymer_insights(batch_doc, material_code, header_name, quantity):
    """Update batch insights for polymers."""
    for polymer_row in batch_doc.batch_polymer_insights:
        if polymer_row.polymer == material_code:
            if header_name == Batch_Insight_Headers.ISSUED.value:
                polymer_row.issued_qty += quantity
            elif header_name == Batch_Insight_Headers.CONSUMED.value:
                polymer_row.consumed_qty += quantity
            elif header_name == Batch_Insight_Headers.REMAINING.value:
                polymer_row.remaining_qty += quantity

def update_blend_insights(batch_doc, material_code, header_name, quantity):
    """Update batch insights for blends."""
    for blend_row in batch_doc.blend_insights:
        if blend_row.enabled:
            if header_name == Batch_Insight_Headers.ISSUED.value:
                blend_row.issued_qty += quantity
            elif header_name == Batch_Insight_Headers.CONSUMED.value:
                blend_row.consumed_qty += quantity
            elif header_name == Batch_Insight_Headers.REMAINING.value:
                blend_row.remaining_qty += quantity

def update_pallet_insights(batch_doc, material_code, header_name, quantity):
    """Update batch insights for pallets."""
    if batch_doc.pallet_code == material_code:
        if header_name == Batch_Insight_Headers.ISSUED.value:
            batch_doc.pallet_issued_qty += quantity
        elif header_name == Batch_Insight_Headers.CONSUMED.value:
            batch_doc.pallet_consumed_qty += quantity
        elif header_name == Batch_Insight_Headers.REMAINING.value:
            batch_doc.pallet_remaining_qty += quantity


def fetch_batch_insights(batch, material_type, header_name, material_code=None):
    """
    Fetch batch insights for a given batch and material.

    Args:
        batch (str): Batch document name.
        material_type (Material_Type): Type of material (e.g., Bag, Polymer, Blend, Pallet).
        header_name (Batch_Insight_Headers): Name of the header (e.g., Issued, Consumed, Damaged, Remaining).
        material_code (str, optional): Code identifying the specific material.

    Returns:
        float: Quantity of the specified header_name.
    """
    batch_doc = frappe.get_doc("Batch", batch)

    if material_type == Material_Type.BAG:
        return get_bag_insight(batch_doc, material_code, header_name)
    elif material_type == Material_Type.POLYMER:
        return get_polymer_insight(batch_doc, material_code, header_name)
    elif material_type == Material_Type.BLEND:
        return get_blend_insight(batch_doc, header_name)
    elif material_type == Material_Type.PALLET:
        return get_pallet_insight(batch_doc, material_code, header_name)

def get_bag_insight(batch_doc, material_code, header_name):
    """Get batch insights for bags."""
    for bag_row in batch_doc.batch_bag_insights:
        if bag_row.bag == material_code:
            return getattr(bag_row, header_name, 0)
    return 0

def get_polymer_insight(batch_doc, material_code, header_name):
    """Get batch insights for polymers."""
    for polymer_row in batch_doc.batch_polymer_insights:
        if polymer_row.polymer == material_code:
            return getattr(polymer_row, header_name, 0)
    return 0

def get_blend_insight(batch_doc, header_name):
    """Get batch insights for blends."""
    total = 0
    for blend_row in batch_doc.blend_insights:
        if blend_row.enabled:
            total += getattr(blend_row, header_name, 0)
    return total

def get_pallet_insight(batch_doc, material_code, header_name):
    """Get batch insights for pallets."""
    if batch_doc.pallet_code == material_code:
        return getattr(batch_doc, f"pallet_{header_name.lower()}_qty", 0)
    return 0

#---------------#

LOSS_PERCENTAGE = 6

def consume_material_for_production(doc, method):
    if method == "on_submit" and doc.status != "Finished":
        frappe.throw("Finish Production to Submit.")

    batch = doc.batch
    production_qty = doc.actual_quantity
    batch_doc = frappe.get_doc("Batch", batch)
    blend_used = ""
    
    #Consume Blend
    for blend in batch_doc.blend_insights:
        if blend.enabled:
            blend_used = blend.blend
            blend_qty_to_consume = calculate_blend_consumed(production_qty)
            #check blend stock
            is_stock_available = check_stock_balance(Material_Type.BLEND.value, 
                                                     blend.blend, 
                                                     Warehouse.BLEND_WAREHOUSE.value, blend_qty_to_consume)
            if not is_stock_available:
                frappe.throw(f"Stock for Blend {blend.blend} Not Available in Warehouse.")

            if method == "on_submit":
                #Create Stock Out Entry for Blend 
                create_stock_entry(
                    stock_entry_for = Material_Type.BLEND.value,
                    stock_entry_item = blend.blend,
                    stock_entry_type = Stock.STOCK_OUT.value,
                    stock_entry_purpose = Stock_Purpose.MATERIAL_CONSUMED.value,
                    source_warehouse = Warehouse.BLEND_WAREHOUSE.value,
                    quantity = blend_qty_to_consume,
                    created_from_doc = "Production",
                    doc_link = doc.name
                )
                

                #Update Blend Consumption
                blend.consumed_qty += blend_qty_to_consume
            
                
            elif method == "on_cancel":
                blend.consumed_qty -= blend_qty_to_consume
				
    #Consume Polymer
    for polymer in batch_doc.batch_polymer_insights:
        if polymer.enabled:
            polymer_qty_to_consume = calculate_polymer_consumption(polymer.required_qty, production_qty)
            #check if issued
            if polymer.issued_qty < polymer_qty_to_consume:
                frappe.throw(f"Not enough quantity of Polymer: {polymer.polymer} is issued for consumption!")
            
            if method == "on_submit":
            #Create stock out entry of polymer from production warehouse
                create_stock_entry(
                    stock_entry_for = "Material",
                    stock_entry_item = polymer.polymer,
                    stock_entry_type = Stock.STOCK_OUT.value,
                    stock_entry_purpose = Stock_Purpose.MATERIAL_CONSUMED.value,
                    source_warehouse = doc.production_warehouse,
                    quantity = polymer_qty_to_consume,
                    created_from_doc = "Production",
                    doc_link = doc.name
                )

                
                #Update Polymer Batch Insights
                polymer.consumed_qty += polymer_qty_to_consume
            
            elif method == "on_cancel":
                polymer.consumed_qty -= polymer_qty_to_consume    
    
    #Consume Bags
    for bag in batch_doc.batch_bag_insights:
        bag_qty_to_consume = calulate_bag_consumption(production_qty, bag.bag_size)
        if bag.issued_qty < bag_qty_to_consume:
            frappe.throw(f"Not enough quantity of material: {bag.bag} is issued for consumption!")
        
        if method == "on_submit":
            #Create stock out entry of polymer from production warehouse
            create_stock_entry(
                    stock_entry_for = "Material",
                    stock_entry_item = bag.bag,
                    stock_entry_type = Stock.STOCK_OUT.value,
                    stock_entry_purpose = Stock_Purpose.MATERIAL_CONSUMED.value,
                    source_warehouse = doc.production_warehouse,
                    quantity = bag_qty_to_consume,
                    created_from_doc = "Production",
                    doc_link = doc.name
                )
            

        #Update Polymer Batch Insights
            bag.consumed_qty += bag_qty_to_consume

        elif method == "on_cancel":
            bag.consumed_qty -= bag_qty_to_consume
    
    if method == "on_submit":
        #Stock In Batch Warehouse
        create_stock_entry(
            stock_entry_for = "Batch",
                    stock_entry_item = doc.batch,
                    stock_entry_type = Stock.STOCK_IN.value,
                    stock_entry_purpose = Stock_Purpose.MANUFACTURE.value,
                    target_warehouse = Warehouse.BATCH_WAREHOUSE.value,
                    quantity = production_qty,
                    created_from_doc = "Production",
                    doc_link = doc.name
                )
        
    
    if method == "on_submit":
        #batch_doc.total_produced_qty += production_qty
        update_batch_stock_breakdown(batch_doc, BSB.TOTAL_PRODUCED_STOCK.value, production_qty)
        prod_progress = (batch_doc.total_produced_qty / batch_doc.total_required_qty) * 100;
        #update_batch_stock_breakdown(batch_doc, BSB.TOTAL_PRODUCTION_PROGRESS.value, prod_progress)
        update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, production_qty)
        update_batch_stock_breakdown(batch_doc, BSB.QC_REMAINING_STOCK.value, production_qty)
        batch_doc.save(ignore_permissions=True)
        batch_doc.production_progress = prod_progress
        if batch_doc.batch_state != Batch_State.PRODUCTION.value:
            batch_doc.batch_state = Batch_State.PRODUCTION.value
        if not doc.external:
            #Generate Machine Logs
            for machine in doc.machines_used:
                generate_machine_log(
                    machine=machine.machine,
                    log_type=Machine_Log_Type.PRODUCTION.value,
                    hours=doc.actual_hours,
                    ref_doc_name=Machine_Log_Type.PRODUCTION.value,
                    ref_doc_link=doc,
                    batch=doc.batch,
                    quantity=production_qty
                )
            #Generate Batch Insights
            doc.batch_insights_row = batchInternalProdInsights(batch_doc, doc.date, production_qty, doc.production_warehouse, doc.shift, blend_used)
            doc.save(ignore_permissions=True)
        elif doc.external:
            doc.batch_insights_row = batchExternalProdInsights(batch_doc, doc.date, production_qty, doc.production_warehouse, blend_used)
            doc.save(ignore_permissions=True)
        
    elif method == "on_cancel":
        #batch_doc.total_produced_qty -= production_qty
        update_batch_stock_breakdown(batch_doc, BSB.TOTAL_PRODUCED_STOCK.value, -production_qty)
        prod_progress = (batch_doc.total_produced_qty / batch_doc.total_required_qty) * 100;
        #update_batch_stock_breakdown(batch_doc, BSB.TOTAL_PRODUCTION_PROGRESS.value, -prod_progress)
        update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, -production_qty)
        update_batch_stock_breakdown(batch_doc, BSB.QC_REMAINING_STOCK.value, -production_qty)
        batch_doc.save(ignore_permissions=True)
        batch_doc.production_progress = prod_progress
        if batch_doc.total_produced_qty == 0:
            batch_doc.batch_state = Batch_State.BLEND_ASSIGNED.value
         #cancel stock entries:
        current_time = now_datetime()
        frappe.db.sql("""UPDATE `tabStock Management` SET docstatus = 2, modified = %s, modified_by = %s WHERE doc_link = %s AND docstatus = 1""", (current_time, frappe.session.user_fullname, doc.name))
        if not doc.external:
            #remove prod_insights
            for prod_entry in batch_doc.internal_production_insights:
                if prod_entry.name == doc.batch_insights_row:
                    batch_doc.internal_production_insights.remove(prod_entry)
                    break

            #cancel machine logs
            frappe.db.sql("""UPDATE `tabMachine Log` SET docstatus = 2, modified = %s, modified_by = %s WHERE reference_doc_link = %s AND docstatus = 1""", (current_time, frappe.session.user_fullname, doc.name))
        elif doc.external:
            for prod_entry in batch_doc.external_production_insights:
                if prod_entry.name == doc.batch_insights_row:
                    batch_doc.external_production_insights.remove(prod_entry)
                    break
        

    # if method == "on_cancel":
    #     #Cancel Stock Entries
    #     for stock_entry_list in stock_entries_list:
    #         try:
    #             stock_entry_list.cancel()
    #         except Exception as e:
    #             frappe.throw(f"Failed to cancel Stock Management Document: {e}")

    #     #Cancel Machine Logs
    #     for machine_log in machine_log_list:
    #         try:
    #             machine_log.cancel()
    #         except Exception as e:
    #             frappe.throw(f"Failed to cancel Stock Management Document: {e}")
    
    batch_doc.save(ignore_permissions=True)
    
def calculate_blend_consumed(product_quantity):
    blend_consumed = product_quantity * (1 + LOSS_PERCENTAGE / 100)
    return round(blend_consumed, 2)
    
def calculate_polymer_consumption(required_qty_per_mt, product_quantity):
    return round(product_quantity * required_qty_per_mt, 2)

def calulate_bag_consumption(product_quantity, bag_size):
    return (product_quantity * 1000) / (bag_size)

def batchInternalProdInsights(batch_doc, date, qty, warehouse, shift, blend):
    row =  batch_doc.append("internal_production_insights", {})
    row.date =  date
    row.qty_produced= qty
    row.warehouse = warehouse  
    row.shift =  shift
    row.blend_used =  blend
    row.save(ignore_permissions=True)
    return row.name

def batchExternalProdInsights(batch_doc, date, qty, warehouse, blend):
    row =  batch_doc.append("external_production_insights", {})
    row.date =  date
    row.qty_produced= qty
    row.warehouse = warehouse  
    row.blend_used =  blend
    row.save(ignore_permissions=True)
    return row.name

def batchTransferInsights(batch, stock_header, other_batch, date, qty):
    row =  batch.append("batch_transfer_insights", {})
    row.date =  date
    row.quantity = qty
    row.stock_in_out = stock_header
    row.from_to_batch =  other_batch
    row.save(ignore_permissions=True)
    return row.name
    
def batchQualityInsights(batch, accepted_qty, rejected_qty, date, qty):

    row =  batch.append("quality_insights", {})
    row.date =  date
    row.quantity = qty
    row.accepted_qty = accepted_qty
    row.rejected_qty =  rejected_qty
    row.save(ignore_permissions=True)
    return row.name

def batchDispatchInsights(batch, date, qty):

    row =  batch.append("delivery_insights", {})
    row.delivery_date =  date
    row.delivered_qty = qty
    row.save(ignore_permissions=True)
    return row.name


def update_batch_stock_breakdown(batch, field_name, qty):
    batch.set(field_name, batch.get(field_name) + qty)