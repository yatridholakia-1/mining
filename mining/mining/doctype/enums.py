from enum import Enum

class Stock(Enum):
    STOCK_OUT = "Stock Out"
    STOCK_IN = "Stock In"
    STOCK_TRANSFER = "Stock Transfer"

class Stock_Purpose(Enum):
    DAMAGE = "Damage"
    DELIVERY = "Delivery"
    MANUFACTURE = "Manufacture"
    MATERIAL_CONSUMED = "Material Consumed"
    MATERIAL_INWARD = "Material Inward"
    MATERIAL_TRANSFER = "Material Transfer For Manufacture"
    MATERIAL_RETURN = "Material Returned To Store"
    BATCH_TRANSFER = "Batch Transfer"

class Warehouse(Enum):
    STORE = "Store"
    BLEND_WAREHOUSE = "Blend Warehouse"
    BATCH_WAREHOUSE = "Batch Warehouse"
    SWELL_WELL_WAREHOUSE = "Swell Well Warehouse"
    GURU_KRUPA_WAREHOUSE = "Guru Krupa Warehouse"
    RAJ_MINERALS = "Raj Minerals"
    OM_INDUSTRIES = "Om Industries"
    READY_MADE_WAREHOUSE = "Ready-Made Warehouse"
    DEAD_STOCK_WAREHOUSE = "Dead-Stock Warehouse"

class Warehouse_Type(Enum):
    PRODUCTION_WAREHOUSE = "Production Warehouse"
    MATERIAL_WAREHOUSE = "Material Warehouse"

class Batch_State(Enum):
    CREATED = "Created"
    BLEND_ASSIGNED = "Blend Assigned"
    PRODUCTION = "Production"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

class Material_Type(Enum):
    PRODUCT = "Product"
    POLYMER = "Polymer"
    LUMPS = "Lumps"
    PALLET = "Pallet"
    BAG = "Bag"
    BLEND = "Blend"

class Material_Transfer_Type(Enum):
    MATERIAL_ISSUE = "Material Issue"
    MATERIAL_RETURN = "Material Return"

class Batch_Insight_Headers(Enum):
    REQUIRED = "Required"
    ISSUED = "Issued"
    CONSUMED = "Consumed"
    DAMAGED = "Damaged"
    REMAINING = "Remaining"

class Machine_Log_Type(Enum):
    PRODUCTION = "Production"
    DOWNTIME = "Downtime"

class BatchTransferInsightsStock(Enum):
    IN = "In (+)"
    OUT = "Out (-)"

    