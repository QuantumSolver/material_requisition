import frappe
from frappe import _
from frappe.utils import today, add_days

@frappe.whitelist()
def get_visual_items(category=None):
    """Get items with images for visual selection"""
    
    filters = {"disabled": 0, "is_stock_item": 1}
    if category:
        filters["item_group"] = category
    
    try:
        items = frappe.get_all(
            "Item",
            filters=filters,
            fields=[
                "item_code", 
                "item_name", 
                "item_group", 
                "image", 
                "description",
                "stock_uom"
            ],
            limit=100,
            order_by="item_name"
        )
        
        # Add default images for common construction items
        for item in items:
            if not item.image:
                item.image = get_default_item_image(item.item_group)
        
        return items
        
    except Exception as e:
        frappe.log_error(f"Get Visual Items Error: {str(e)}")
        return []

def get_default_item_image(item_group):
    """Get default image based on item group"""
    image_map = {
        "Pipes": "/assets/material_requisition/images/pipe.png",
        "Fittings": "/assets/material_requisition/images/fitting.png",
        "Electrical": "/assets/material_requisition/images/electrical.png",
        "Hardware": "/assets/material_requisition/images/hardware.png",
        "Tools": "/assets/material_requisition/images/tools.png",
        "Safety": "/assets/material_requisition/images/safety.png"
    }
    return image_map.get(item_group, "/assets/material_requisition/images/default.png")

@frappe.whitelist()
def create_simplified_material_request(items, project=None, required_date=None, notes=None, required_by_date=None, delivery_date=None):
    """Create material request with simplified workflow"""

    try:
        if not items:
            frappe.throw(_("No items selected"))

        # Parse items if it's a string
        if isinstance(items, str):
            import json
            items = json.loads(items)

        doc = frappe.new_doc("Material Request")
        doc.material_request_type = "Purchase"
        doc.transaction_date = today()

        # Set schedule date (required by date takes priority)
        if required_by_date:
            doc.schedule_date = required_by_date
        elif required_date:
            doc.schedule_date = required_date
        else:
            doc.schedule_date = add_days(today(), 7)

        if project:
            doc.project = project

        # Combine notes with delivery date info
        notes_text = notes or "Created from Promep interface"
        if delivery_date:
            notes_text += f"\nExpected Delivery Date: {delivery_date}"

        doc.remarks = notes_text
        
        # Add items
        for item in items:
            doc.append("items", {
                "item_code": item["item_code"],
                "qty": item["qty"],
                "uom": item.get("uom", "Nos"),
                "schedule_date": doc.schedule_date,
                "warehouse": get_default_warehouse()
            })
        
        doc.insert()
        doc.submit()
        
        return {
            "name": doc.name,
            "status": "success",
            "message": _("Material request created successfully")
        }
        
    except Exception as e:
        frappe.log_error(f"Create Material Request Error: {str(e)}")
        frappe.throw(_("Failed to create material request: {0}").format(str(e)))

def get_default_warehouse():
    """Get default warehouse for material requests"""
    try:
        # Try to get from company settings
        company = frappe.defaults.get_user_default("Company")
        if company:
            company_doc = frappe.get_doc("Company", company)
            if hasattr(company_doc, 'default_warehouse'):
                return company_doc.default_warehouse
        
        # Fallback to first available warehouse
        warehouse = frappe.get_all("Warehouse", limit=1)
        if warehouse:
            return warehouse[0].name
            
        return None
        
    except Exception:
        return None

@frappe.whitelist()
def get_material_request_details(name):
    """Get detailed information about a material request"""
    
    try:
        doc = frappe.get_doc("Material Request", name)
        
        # Get items with additional details
        items = []
        for item in doc.items:
            items.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "uom": item.uom,
                "ordered_qty": item.ordered_qty,
                "received_qty": item.received_qty,
                "rate": item.rate,
                "amount": item.amount
            })
        
        return {
            "name": doc.name,
            "transaction_date": doc.transaction_date,
            "schedule_date": doc.schedule_date,
            "status": doc.status,
            "per_ordered": doc.per_ordered,
            "per_received": doc.per_received,
            "project": doc.project,
            "remarks": doc.remarks,
            "items": items,
            "total_qty": doc.total_qty
        }
        
    except Exception as e:
        frappe.log_error(f"Get Material Request Details Error: {str(e)}")
        frappe.throw(_("Failed to get material request details"))

@frappe.whitelist()
def get_suppliers_for_items(item_codes):
    """Get suppliers for given item codes"""

    try:
        if isinstance(item_codes, str):
            import json
            item_codes = json.loads(item_codes)

        suppliers = frappe.get_all(
            "Item Supplier",
            filters={"parent": ["in", item_codes]},
            fields=["supplier", "supplier_name", "parent as item_code"],
            group_by="supplier"
        )

        # Also get general suppliers
        all_suppliers = frappe.get_all(
            "Supplier",
            filters={"disabled": 0},
            fields=["name", "supplier_name"],
            limit=20
        )

        return {
            "item_suppliers": suppliers,
            "all_suppliers": all_suppliers
        }

    except Exception as e:
        frappe.log_error(f"Get Suppliers Error: {str(e)}")
        return {"item_suppliers": [], "all_suppliers": []}

@frappe.whitelist()
def get_requests_with_po_status():
    """Get material requests with purchase order status"""

    try:
        # Get material requests
        requests = frappe.get_all(
            "Material Request",
            filters={"docstatus": 1},
            fields=[
                "name", "transaction_date", "schedule_date", "status",
                "per_ordered", "per_received", "company", "material_request_type",
                "owner", "creation"
            ],
            order_by="creation desc",
            limit=50
        )

        # Get items for each request
        for request in requests:
            request["items"] = frappe.get_all(
                "Material Request Item",
                filters={"parent": request["name"]},
                fields=[
                    "item_code", "item_name", "qty", "uom",
                    "ordered_qty", "received_qty", "rate", "amount"
                ]
            )

            # Get related purchase orders
            request["purchase_orders"] = get_purchase_orders_for_request(request["name"])

        return requests

    except Exception as e:
        frappe.log_error(f"Get Requests with PO Status Error: {str(e)}")
        return []

@frappe.whitelist()
def get_request_detail(request_name):
    """Get detailed information about a specific material request"""

    try:
        doc = frappe.get_doc("Material Request", request_name)

        # Get items with additional details
        items = []
        for item in doc.items:
            items.append({
                "item_code": item.item_code,
                "item_name": getattr(item, 'item_name', ''),
                "description": getattr(item, 'description', ''),
                "qty": item.qty,
                "uom": getattr(item, 'uom', ''),
                "ordered_qty": getattr(item, 'ordered_qty', 0),
                "received_qty": getattr(item, 'received_qty', 0),
                "rate": getattr(item, 'rate', 0),
                "amount": getattr(item, 'amount', 0)
            })

        # Get related purchase orders
        purchase_orders = get_purchase_orders_for_request(request_name)

        # Calculate total quantity
        total_qty = sum(item.qty for item in doc.items)

        return {
            "name": doc.name,
            "transaction_date": doc.transaction_date,
            "schedule_date": getattr(doc, 'schedule_date', None),
            "status": doc.status,
            "per_ordered": getattr(doc, 'per_ordered', 0),
            "per_received": getattr(doc, 'per_received', 0),
            "material_request_type": getattr(doc, 'material_request_type', ''),
            "company": getattr(doc, 'company', ''),
            "items": items,
            "total_qty": total_qty,
            "purchase_orders": purchase_orders
        }

    except Exception as e:
        frappe.log_error(f"Get Request Detail Error: {str(e)}")
        return {"error": f"Failed to get request details: {str(e)}"}

def get_purchase_orders_for_request(material_request_name):
    """Get purchase orders related to a material request"""

    try:
        # Get PO items that reference this material request
        po_items = frappe.get_all(
            "Purchase Order Item",
            filters={"material_request": material_request_name},
            fields=["parent"],
            group_by="parent"
        )

        if not po_items:
            return []

        po_names = [item["parent"] for item in po_items]

        # Get PO details
        purchase_orders = frappe.get_all(
            "Purchase Order",
            filters={"name": ["in", po_names]},
            fields=[
                "name", "supplier", "supplier_name", "transaction_date",
                "status", "grand_total", "currency"
            ]
        )

        return purchase_orders

    except Exception as e:
        frappe.log_error(f"Get Purchase Orders for Request Error: {str(e)}")
        return []
