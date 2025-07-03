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

@frappe.whitelist()
def get_line_items(status_filter=None, item_filter=None, supplier_filter=None, limit=100, offset=0):
    """Get all line items from material requests with filtering options"""

    try:

        # Build base query conditions
        conditions = ["mr.docstatus = 1"]

        # Add status filter
        if status_filter and status_filter != 'all':
            if status_filter == 'pending':
                conditions.append("(mr.per_ordered = 0 OR mr.per_ordered IS NULL)")
            elif status_filter == 'partial':
                conditions.append("mr.per_ordered > 0 AND mr.per_ordered < 100")
            elif status_filter == 'ordered':
                conditions.append("mr.per_ordered = 100 AND (mr.per_received < 100 OR mr.per_received IS NULL)")
            elif status_filter == 'received':
                conditions.append("mr.per_received = 100")

        # Add item filter
        if item_filter:
            conditions.append(f"(mri.item_code LIKE '%{item_filter}%' OR mri.item_name LIKE '%{item_filter}%')")

        where_clause = " AND ".join(conditions)

        # Get line items with material request details
        query = f"""
            SELECT
                mri.name as line_item_id,
                mri.item_code,
                mri.item_name,
                mri.description,
                mri.qty,
                mri.uom,
                COALESCE(mri.ordered_qty, 0) as ordered_qty,
                COALESCE(mri.received_qty, 0) as received_qty,
                mri.rate,
                mri.amount,
                mri.schedule_date as item_schedule_date,
                mr.name as material_request,
                mr.transaction_date,
                mr.schedule_date as request_schedule_date,
                mr.status as request_status,
                COALESCE(mr.per_ordered, 0) as per_ordered,
                COALESCE(mr.per_received, 0) as per_received,
                mr.company,
                mr.owner as requested_by,
                (mri.qty - COALESCE(mri.ordered_qty, 0)) as pending_qty,
                CASE
                    WHEN COALESCE(mri.received_qty, 0) >= mri.qty THEN 'received'
                    WHEN COALESCE(mri.ordered_qty, 0) >= mri.qty THEN 'ordered'
                    WHEN COALESCE(mri.ordered_qty, 0) > 0 THEN 'partial'
                    ELSE 'pending'
                END as item_status
            FROM `tabMaterial Request Item` mri
            LEFT JOIN `tabMaterial Request` mr ON mri.parent = mr.name
            WHERE {where_clause}
            ORDER BY mr.creation DESC, mri.idx ASC
            LIMIT {int(limit)} OFFSET {int(offset)}
        """

        line_items = frappe.db.sql(query, as_dict=True)

        # Get supplier information for items that have suppliers
        item_codes = [item['item_code'] for item in line_items]
        if item_codes:
            suppliers_query = """
                SELECT
                    itsup.parent as item_code,
                    itsup.supplier,
                    sup.supplier_name
                FROM `tabItem Supplier` itsup
                LEFT JOIN `tabSupplier` sup ON itsup.supplier = sup.name
                WHERE itsup.parent IN %(item_codes)s
                GROUP BY itsup.parent, itsup.supplier
            """
            suppliers_data = frappe.db.sql(suppliers_query, {"item_codes": item_codes}, as_dict=True)

            # Create a mapping of item_code to suppliers
            item_suppliers = {}
            for supplier_data in suppliers_data:
                item_code = supplier_data['item_code']
                if item_code not in item_suppliers:
                    item_suppliers[item_code] = []
                item_suppliers[item_code].append({
                    'supplier': supplier_data['supplier'],
                    'supplier_name': supplier_data['supplier_name'] or supplier_data['supplier']
                })
        else:
            item_suppliers = {}

        # Add supplier information to line items
        for item in line_items:
            item['suppliers'] = item_suppliers.get(item['item_code'], [])
            # Calculate item status based on quantities
            if item['received_qty'] >= item['qty']:
                item['item_status'] = 'received'
            elif item['ordered_qty'] >= item['qty']:
                item['item_status'] = 'ordered'
            elif item['ordered_qty'] > 0:
                item['item_status'] = 'partial'
            else:
                item['item_status'] = 'pending'

        # Get total count for pagination
        count_query = f"""
            SELECT COUNT(*) as total
            FROM `tabMaterial Request Item` mri
            LEFT JOIN `tabMaterial Request` mr ON mri.parent = mr.name
            WHERE {where_clause}
        """
        total_count = frappe.db.sql(count_query, as_dict=True)[0]['total']

        return {
            'line_items': line_items,
            'total_count': total_count,
            'has_more': (int(offset) + len(line_items)) < total_count
        }

    except Exception as e:
        frappe.log_error(f"Get All Line Items Error: {str(e)}")
        return {'line_items': [], 'total_count': 0, 'has_more': False}

@frappe.whitelist()
def get_request_detail(request_name):
    """Get detailed information about a specific material request"""
    try:
        # Get the material request
        mr = frappe.get_doc("Material Request", request_name)

        # Check permissions
        if not frappe.has_permission("Material Request", "read", mr):
            frappe.throw("Not permitted to read this Material Request")

        # Get related purchase orders
        purchase_orders = frappe.db.sql("""
            SELECT DISTINCT po.name, po.supplier, po.transaction_date,
                   po.status, po.grand_total
            FROM `tabPurchase Order` po
            JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
            WHERE poi.material_request = %s AND po.docstatus = 1
            ORDER BY po.creation DESC
        """, (request_name,), as_dict=True)

        # Prepare response data
        result = {
            'name': mr.name,
            'transaction_date': mr.transaction_date,
            'schedule_date': mr.schedule_date,
            'status': mr.status,
            'per_ordered': mr.per_ordered,
            'per_received': mr.per_received,
            'company': mr.company,
            'remarks': getattr(mr, 'remarks', None),
            'items': [],
            'purchase_orders': purchase_orders
        }

        # Add items
        for item in mr.items:
            result['items'].append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'description': item.description,
                'qty': item.qty,
                'uom': item.uom,
                'ordered_qty': item.ordered_qty or 0,
                'received_qty': item.received_qty or 0,
                'rate': item.rate,
                'amount': item.amount,
                'schedule_date': item.schedule_date
            })

        return result

    except Exception as e:
        frappe.log_error(f"Get Request Detail Error: {str(e)}")
        frappe.throw(f"Failed to get request details: {str(e)}")

@frappe.whitelist()
def test_line_items_debug():
    """Debug function to test line items query"""
    try:
        # Test 1: Count all material requests
        mr_count = frappe.db.sql("SELECT COUNT(*) as count FROM `tabMaterial Request`", as_dict=True)[0]['count']

        # Test 2: Count submitted material requests
        mr_submitted = frappe.db.sql("SELECT COUNT(*) as count FROM `tabMaterial Request` WHERE docstatus = 1", as_dict=True)[0]['count']

        # Test 3: Count all material request items
        mri_count = frappe.db.sql("SELECT COUNT(*) as count FROM `tabMaterial Request Item`", as_dict=True)[0]['count']

        # Test 4: Count items from submitted requests
        mri_submitted = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabMaterial Request Item` mri
            LEFT JOIN `tabMaterial Request` mr ON mri.parent = mr.name
            WHERE mr.docstatus = 1
        """, as_dict=True)[0]['count']

        # Test 5: Get sample data
        sample_data = frappe.db.sql("""
            SELECT mri.name, mri.item_code, mr.name as mr_name, mr.docstatus
            FROM `tabMaterial Request Item` mri
            LEFT JOIN `tabMaterial Request` mr ON mri.parent = mr.name
            WHERE mr.docstatus = 1
            LIMIT 3
        """, as_dict=True)

        return {
            'total_mr': mr_count,
            'submitted_mr': mr_submitted,
            'total_mri': mri_count,
            'submitted_mri': mri_submitted,
            'sample_data': sample_data
        }

    except Exception as e:
        return {'error': str(e)}

@frappe.whitelist()
def test_line_items():
    """Simple test function to check if whitelisting works"""
    return {"message": "Line items API is working!", "test": True}
