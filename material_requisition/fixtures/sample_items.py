import frappe

def create_sample_items():
    """Create sample construction items for testing"""
    
    sample_items = [
        {
            "item_code": "PIPE-PVC-4IN",
            "item_name": "PVC Pipe 4 inch",
            "item_group": "Pipes",
            "stock_uom": "Meter",
            "description": "4 inch PVC pipe for plumbing"
        },
        {
            "item_code": "ELBOW-PVC-4IN",
            "item_name": "PVC Elbow 4 inch",
            "item_group": "Fittings",
            "stock_uom": "Nos",
            "description": "4 inch PVC elbow joint"
        },
        {
            "item_code": "WIRE-COPPER-12AWG",
            "item_name": "Copper Wire 12 AWG",
            "item_group": "Electrical",
            "stock_uom": "Meter",
            "description": "12 AWG copper electrical wire"
        },
        {
            "item_code": "SCREW-WOOD-2IN",
            "item_name": "Wood Screw 2 inch",
            "item_group": "Hardware",
            "stock_uom": "Nos",
            "description": "2 inch wood screws"
        },
        {
            "item_code": "HAMMER-CLAW",
            "item_name": "Claw Hammer",
            "item_group": "Tools",
            "stock_uom": "Nos",
            "description": "Standard claw hammer"
        },
        {
            "item_code": "HELMET-SAFETY",
            "item_name": "Safety Helmet",
            "item_group": "Safety",
            "stock_uom": "Nos",
            "description": "Construction safety helmet"
        },
        {
            "item_code": "CEMENT-BAG-50KG",
            "item_name": "Cement Bag 50kg",
            "item_group": "Materials",
            "stock_uom": "Nos",
            "description": "50kg cement bag"
        },
        {
            "item_code": "REBAR-10MM",
            "item_name": "Rebar 10mm",
            "item_group": "Materials",
            "stock_uom": "Meter",
            "description": "10mm steel rebar"
        }
    ]
    
    for item_data in sample_items:
        if not frappe.db.exists("Item", item_data["item_code"]):
            item = frappe.new_doc("Item")
            item.update(item_data)
            item.is_stock_item = 1
            item.include_item_in_manufacturing = 0
            item.insert()
            print(f"Created item: {item.item_code}")
        else:
            print(f"Item already exists: {item_data['item_code']}")

def create_sample_suppliers():
    """Create sample suppliers for testing"""
    
    sample_suppliers = [
        {
            "supplier_name": "ABC Construction Supplies",
            "supplier_group": "Hardware"
        },
        {
            "supplier_name": "XYZ Electrical Supplies",
            "supplier_group": "Electrical"
        },
        {
            "supplier_name": "BuildMart Materials",
            "supplier_group": "Materials"
        }
    ]
    
    for supplier_data in sample_suppliers:
        if not frappe.db.exists("Supplier", supplier_data["supplier_name"]):
            supplier = frappe.new_doc("Supplier")
            supplier.update(supplier_data)
            supplier.insert()
            print(f"Created supplier: {supplier.supplier_name}")
        else:
            print(f"Supplier already exists: {supplier_data['supplier_name']}")

if __name__ == "__main__":
    create_sample_items()
    create_sample_suppliers()
    frappe.db.commit()
