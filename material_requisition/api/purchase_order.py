import frappe
from frappe import _
from frappe.utils import today, add_days

@frappe.whitelist()
def create_purchase_order_from_material_request(material_request, supplier, required_date=None):
    """Create purchase order from material request with simplified workflow"""
    
    try:
        if not material_request or not supplier:
            frappe.throw(_("Material Request and Supplier are required"))
        
        # Get material request document
        mr_doc = frappe.get_doc("Material Request", material_request)
        
        # Create purchase order
        po_doc = frappe.new_doc("Purchase Order")
        po_doc.supplier = supplier
        po_doc.transaction_date = today()
        po_doc.schedule_date = required_date or add_days(today(), 7)
        po_doc.company = mr_doc.company
        
        # Add items from material request
        for mr_item in mr_doc.items:
            if mr_item.ordered_qty < mr_item.qty:  # Only add items that are not fully ordered
                remaining_qty = mr_item.qty - mr_item.ordered_qty
                
                po_doc.append("items", {
                    "item_code": mr_item.item_code,
                    "qty": remaining_qty,
                    "uom": mr_item.uom,
                    "schedule_date": po_doc.schedule_date,
                    "material_request": mr_doc.name,
                    "material_request_item": mr_item.name,
                    "warehouse": mr_item.warehouse
                })
        
        if not po_doc.items:
            frappe.throw(_("No items to order from this material request"))
        
        po_doc.insert()
        po_doc.submit()
        
        return {
            "name": po_doc.name,
            "status": "success",
            "message": _("Purchase order created successfully")
        }
        
    except Exception as e:
        frappe.log_error(f"Create Purchase Order Error: {str(e)}")
        frappe.throw(_("Failed to create purchase order: {0}").format(str(e)))

@frappe.whitelist()
def get_pending_material_requests():
    """Get material requests that are pending purchase orders"""
    
    try:
        requests = frappe.db.sql("""
            SELECT 
                mr.name,
                mr.transaction_date,
                mr.schedule_date,
                mr.per_ordered,
                COUNT(mri.name) as item_count,
                SUM(mri.qty - mri.ordered_qty) as pending_qty
            FROM `tabMaterial Request` mr
            LEFT JOIN `tabMaterial Request Item` mri ON mr.name = mri.parent
            WHERE mr.docstatus = 1 
                AND mr.material_request_type = 'Purchase'
                AND mr.per_ordered < 100
            GROUP BY mr.name
            ORDER BY mr.creation DESC
        """, as_dict=True)
        
        # Get items for each request
        for request in requests:
            items = frappe.get_all(
                "Material Request Item",
                filters={
                    "parent": request.name,
                    "qty": [">", "ordered_qty"]
                },
                fields=[
                    "item_code",
                    "item_name", 
                    "qty",
                    "ordered_qty",
                    "uom"
                ]
            )
            request.items = items
        
        return requests
        
    except Exception as e:
        frappe.log_error(f"Get Pending Material Requests Error: {str(e)}")
        return []

@frappe.whitelist()
def bulk_create_purchase_orders(requests_data):
    """Create multiple purchase orders from material requests"""
    
    try:
        if isinstance(requests_data, str):
            import json
            requests_data = json.loads(requests_data)
        
        results = []
        
        for request_data in requests_data:
            try:
                result = create_purchase_order_from_material_request(
                    request_data.get("material_request"),
                    request_data.get("supplier"),
                    request_data.get("required_date")
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "material_request": request_data.get("material_request"),
                    "status": "error",
                    "message": str(e)
                })
        
        return results
        
    except Exception as e:
        frappe.log_error(f"Bulk Create Purchase Orders Error: {str(e)}")
        frappe.throw(_("Failed to create purchase orders"))

@frappe.whitelist()
def get_purchase_order_status(material_request):
    """Get purchase order status for a material request"""
    
    try:
        # Get purchase orders linked to this material request
        purchase_orders = frappe.db.sql("""
            SELECT DISTINCT po.name, po.status, po.per_received, po.supplier
            FROM `tabPurchase Order` po
            LEFT JOIN `tabPurchase Order Item` poi ON po.name = poi.parent
            WHERE poi.material_request = %s
                AND po.docstatus = 1
        """, (material_request,), as_dict=True)
        
        return purchase_orders
        
    except Exception as e:
        frappe.log_error(f"Get Purchase Order Status Error: {str(e)}")
        return []

@frappe.whitelist()
def update_material_request_status():
    """Update material request status based on purchase orders and receipts"""

    try:
        # This would typically be called by a scheduled job
        # Update per_ordered and per_received for all material requests

        material_requests = frappe.get_all(
            "Material Request",
            filters={"docstatus": 1, "material_request_type": "Purchase"},
            fields=["name"]
        )

        for mr in material_requests:
            mr_doc = frappe.get_doc("Material Request", mr.name)
            mr_doc.update_status()
            mr_doc.save()

        return {"status": "success", "message": "Status updated for all material requests"}

    except Exception as e:
        frappe.log_error(f"Update Material Request Status Error: {str(e)}")
        frappe.throw(_("Failed to update material request status"))

@frappe.whitelist()
def get_suppliers():
    """Get all active suppliers for dropdown selection"""

    try:
        suppliers = frappe.get_all(
            "Supplier",
            filters={"disabled": 0},
            fields=["name", "supplier_name", "supplier_group", "country"],
            order_by="supplier_name",
            limit=100
        )

        return suppliers

    except Exception as e:
        frappe.log_error(f"Get Suppliers Error: {str(e)}")
        return []

@frappe.whitelist()
def create_from_material_request(material_request, supplier, required_date=None, notes=None):
    """Enhanced PO creation with additional options"""

    try:
        if not material_request or not supplier:
            frappe.throw(_("Material Request and Supplier are required"))

        # Get material request document
        mr_doc = frappe.get_doc("Material Request", material_request)

        # Validate supplier exists
        if not frappe.db.exists("Supplier", supplier):
            frappe.throw(_("Invalid supplier selected"))

        # Create purchase order
        po_doc = frappe.new_doc("Purchase Order")
        po_doc.supplier = supplier
        po_doc.transaction_date = today()
        po_doc.schedule_date = required_date or add_days(today(), 14)
        po_doc.company = mr_doc.company or frappe.defaults.get_user_default("Company")

        if notes:
            po_doc.remarks = notes

        # Add items from material request
        items_added = 0
        for mr_item in mr_doc.items:
            if mr_item.ordered_qty < mr_item.qty:  # Only add items that are not fully ordered
                remaining_qty = mr_item.qty - mr_item.ordered_qty

                po_doc.append("items", {
                    "item_code": mr_item.item_code,
                    "qty": remaining_qty,
                    "uom": mr_item.uom,
                    "schedule_date": po_doc.schedule_date,
                    "material_request": mr_doc.name,
                    "material_request_item": mr_item.name,
                    "warehouse": mr_item.warehouse or get_default_warehouse()
                })
                items_added += 1

        if items_added == 0:
            frappe.throw(_("No items available to order from this material request"))

        # Insert and submit
        po_doc.insert()
        po_doc.submit()

        return {
            "name": po_doc.name,
            "status": "success",
            "message": _("Purchase order {0} created successfully with {1} items").format(po_doc.name, items_added),
            "items_count": items_added,
            "grand_total": po_doc.grand_total
        }

    except Exception as e:
        frappe.log_error(f"Enhanced Create Purchase Order Error: {str(e)}")
        frappe.throw(_("Failed to create purchase order: {0}").format(str(e)))

def get_default_warehouse():
    """Get default warehouse for purchase orders"""
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
def get_po_summary_for_requests(material_requests):
    """Get purchase order summary for multiple material requests"""

    try:
        if isinstance(material_requests, str):
            import json
            material_requests = json.loads(material_requests)

        if not material_requests:
            return []

        # Get PO summary for each material request
        summary = []
        for mr_name in material_requests:
            po_data = frappe.db.sql("""
                SELECT
                    po.name,
                    po.supplier,
                    po.supplier_name,
                    po.status,
                    po.grand_total,
                    po.transaction_date,
                    COUNT(poi.name) as item_count
                FROM `tabPurchase Order` po
                LEFT JOIN `tabPurchase Order Item` poi ON po.name = poi.parent
                WHERE poi.material_request = %s
                    AND po.docstatus = 1
                GROUP BY po.name
                ORDER BY po.creation DESC
            """, (mr_name,), as_dict=True)

            summary.append({
                "material_request": mr_name,
                "purchase_orders": po_data
            })

        return summary

    except Exception as e:
        frappe.log_error(f"Get PO Summary Error: {str(e)}")
        return []
