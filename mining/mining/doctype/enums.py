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

    