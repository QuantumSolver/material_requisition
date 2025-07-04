import frappe
from frappe import _

@frappe.whitelist()
def get_purchase_receipts(status_filter=None, supplier_filter=None, limit=50, offset=0):
    """Get purchase receipts with filtering options"""
    
    try:
        # Build base query conditions
        conditions = ["pr.docstatus IN (0, 1, 2)"]  # Include all statuses
        
        # Add status filter
        if status_filter and status_filter != 'all':
            if status_filter == 'draft':
                conditions.append("pr.docstatus = 0")
            elif status_filter == 'submitted':
                conditions.append("pr.docstatus = 1")
            elif status_filter == 'cancelled':
                conditions.append("pr.docstatus = 2")
        
        # Add supplier filter
        if supplier_filter:
            conditions.append(f"pr.supplier LIKE '%{supplier_filter}%'")
        
        where_clause = " AND ".join(conditions)
        
        # Get purchase receipts with related information
        query = f"""
            SELECT
                pr.name,
                pr.supplier,
                pr.posting_date,
                pr.posting_time,
                pr.status,
                pr.docstatus,
                pr.grand_total,
                pr.currency,
                pr.company,
                pr.remarks,
                pr.creation,
                pr.modified,
                pr.owner,
                COUNT(pri.name) as total_items,
                SUM(pri.qty) as total_qty,
                SUM(pri.received_qty) as total_received_qty,
                CASE
                    WHEN pr.docstatus = 0 THEN 'Draft'
                    WHEN pr.docstatus = 1 THEN 'Submitted'
                    WHEN pr.docstatus = 2 THEN 'Cancelled'
                    ELSE 'Unknown'
                END as receipt_status
            FROM `tabPurchase Receipt` pr
            LEFT JOIN `tabPurchase Receipt Item` pri ON pri.parent = pr.name
            WHERE {where_clause}
            GROUP BY pr.name
            ORDER BY pr.creation DESC
            LIMIT {int(limit)} OFFSET {int(offset)}
        """
        
        receipts = frappe.db.sql(query, as_dict=True)
        
        # Get total count for pagination
        count_query = f"""
            SELECT COUNT(DISTINCT pr.name) as total_count
            FROM `tabPurchase Receipt` pr
            WHERE {where_clause}
        """
        total_count = frappe.db.sql(count_query, as_dict=True)[0]['total_count']
        
        # Get related purchase orders for each receipt
        for receipt in receipts:
            po_query = """
                SELECT DISTINCT pri.purchase_order
                FROM `tabPurchase Receipt Item` pri
                WHERE pri.parent = %s AND pri.purchase_order IS NOT NULL
            """
            pos = frappe.db.sql(po_query, (receipt['name'],), as_dict=True)
            receipt['purchase_orders'] = [po['purchase_order'] for po in pos if po['purchase_order']]
        
        has_more = (int(offset) + len(receipts)) < total_count
        
        return {
            'receipts': receipts,
            'total_count': total_count,
            'has_more': has_more
        }
        
    except Exception as e:
        frappe.log_error(f"Get Purchase Receipts Error: {str(e)}")
        return {'receipts': [], 'total_count': 0, 'has_more': False}

@frappe.whitelist()
def get_receipt_detail(receipt_name):
    """Get detailed information about a specific purchase receipt"""
    
    try:
        # Get the purchase receipt
        pr = frappe.get_doc("Purchase Receipt", receipt_name)
        
        # Check permissions
        if not frappe.has_permission("Purchase Receipt", "read", pr):
            frappe.throw("Not permitted to read this Purchase Receipt")
        
        # Get related material requests
        material_requests = frappe.db.sql("""
            SELECT DISTINCT pri.material_request
            FROM `tabPurchase Receipt Item` pri
            WHERE pri.parent = %s AND pri.material_request IS NOT NULL
        """, (receipt_name,), as_dict=True)
        
        # Get related purchase orders
        purchase_orders = frappe.db.sql("""
            SELECT DISTINCT pri.purchase_order, po.supplier, po.transaction_date, po.status
            FROM `tabPurchase Receipt Item` pri
            LEFT JOIN `tabPurchase Order` po ON pri.purchase_order = po.name
            WHERE pri.parent = %s AND pri.purchase_order IS NOT NULL
        """, (receipt_name,), as_dict=True)
        
        # Prepare response data
        result = {
            'name': pr.name,
            'supplier': pr.supplier,
            'posting_date': pr.posting_date,
            'posting_time': pr.posting_time,
            'status': pr.status,
            'docstatus': pr.docstatus,
            'grand_total': pr.grand_total,
            'currency': pr.currency,
            'company': pr.company,
            'remarks': pr.remarks,
            'creation': pr.creation,
            'modified': pr.modified,
            'owner': pr.owner,
            'items': [],
            'material_requests': [mr['material_request'] for mr in material_requests if mr['material_request']],
            'purchase_orders': purchase_orders
        }
        
        # Add items
        for item in pr.items:
            result['items'].append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'description': item.description,
                'qty': item.qty,
                'received_qty': item.received_qty,
                'uom': item.uom,
                'rate': item.rate,
                'amount': item.amount,
                'purchase_order': item.purchase_order,
                'material_request': item.material_request,
                'warehouse': item.warehouse,
                'batch_no': getattr(item, 'batch_no', None),
                'serial_no': getattr(item, 'serial_no', None)
            })
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Get Receipt Detail Error: {str(e)}")
        frappe.throw(f"Failed to get receipt details: {str(e)}")

@frappe.whitelist()
def get_receipts_for_material_request(material_request_name):
    """Get purchase receipts related to a specific material request"""
    
    try:
        query = """
            SELECT DISTINCT
                pr.name,
                pr.supplier,
                pr.posting_date,
                pr.status,
                pr.docstatus,
                pr.grand_total,
                SUM(pri.received_qty) as total_received_qty,
                CASE
                    WHEN pr.docstatus = 0 THEN 'Draft'
                    WHEN pr.docstatus = 1 THEN 'Submitted'
                    WHEN pr.docstatus = 2 THEN 'Cancelled'
                    ELSE 'Unknown'
                END as receipt_status
            FROM `tabPurchase Receipt` pr
            JOIN `tabPurchase Receipt Item` pri ON pri.parent = pr.name
            WHERE pri.material_request = %s
            GROUP BY pr.name
            ORDER BY pr.creation DESC
        """
        
        receipts = frappe.db.sql(query, (material_request_name,), as_dict=True)
        
        return {'receipts': receipts}
        
    except Exception as e:
        frappe.log_error(f"Get Receipts for Material Request Error: {str(e)}")
        return {'receipts': []}

@frappe.whitelist()
def get_receipts_for_purchase_order(purchase_order_name):
    """Get purchase receipts related to a specific purchase order"""
    
    try:
        query = """
            SELECT DISTINCT
                pr.name,
                pr.supplier,
                pr.posting_date,
                pr.status,
                pr.docstatus,
                pr.grand_total,
                SUM(pri.received_qty) as total_received_qty,
                CASE
                    WHEN pr.docstatus = 0 THEN 'Draft'
                    WHEN pr.docstatus = 1 THEN 'Submitted'
                    WHEN pr.docstatus = 2 THEN 'Cancelled'
                    ELSE 'Unknown'
                END as receipt_status
            FROM `tabPurchase Receipt` pr
            JOIN `tabPurchase Receipt Item` pri ON pri.parent = pr.name
            WHERE pri.purchase_order = %s
            GROUP BY pr.name
            ORDER BY pr.creation DESC
        """
        
        receipts = frappe.db.sql(query, (purchase_order_name,), as_dict=True)
        
        return {'receipts': receipts}
        
    except Exception as e:
        frappe.log_error(f"Get Receipts for Purchase Order Error: {str(e)}")
        return {'receipts': []}
