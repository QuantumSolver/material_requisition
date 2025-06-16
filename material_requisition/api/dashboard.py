import frappe
from frappe import _

@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard statistics and recent requests"""
    
    try:
        # Get status counts
        status_counts = frappe.db.sql("""
            SELECT 
                CASE 
                    WHEN per_ordered = 0 THEN 'pending'
                    WHEN per_ordered = 100 AND per_received < 100 THEN 'ordered'
                    WHEN per_ordered > 0 AND per_ordered < 100 THEN 'partial'
                    WHEN per_received = 100 THEN 'received'
                    ELSE 'pending'
                END as status,
                COUNT(*) as count
            FROM `tabMaterial Request`
            WHERE docstatus = 1
            GROUP BY status
        """, as_dict=True)
        
        # Get recent requests
        recent_requests = frappe.get_all(
            "Material Request",
            filters={"docstatus": 1},
            fields=[
                "name", 
                "transaction_date", 
                "per_ordered", 
                "per_received",
                "creation",
                "modified"
            ],
            order_by="creation desc",
            limit=10
        )
        
        # Add status to recent requests
        for request in recent_requests:
            if request.per_received == 100:
                request.status = 'received'
            elif request.per_ordered == 100:
                request.status = 'ordered'
            elif request.per_ordered > 0:
                request.status = 'partial'
            else:
                request.status = 'pending'
        
        return {
            "status_counts": status_counts,
            "recent_requests": recent_requests
        }
        
    except Exception as e:
        frappe.log_error(f"Dashboard API Error: {str(e)}")
        return {
            "status_counts": [
                {"status": "pending", "count": 0},
                {"status": "ordered", "count": 0},
                {"status": "partial", "count": 0},
                {"status": "received", "count": 0}
            ],
            "recent_requests": []
        }

@frappe.whitelist()
def get_material_requests_by_status(status=None):
    """Get material requests filtered by status"""
    
    filters = {"docstatus": 1}
    
    if status == 'pending':
        filters["per_ordered"] = 0
    elif status == 'ordered':
        filters["per_ordered"] = 100
        filters["per_received"] = ["<", 100]
    elif status == 'partial':
        filters["per_ordered"] = [">", 0]
        filters["per_ordered"] = ["<", 100]
    elif status == 'received':
        filters["per_received"] = 100
    
    requests = frappe.get_all(
        "Material Request",
        filters=filters,
        fields=[
            "name",
            "transaction_date",
            "per_ordered",
            "per_received",
            "total_qty",
            "creation"
        ],
        order_by="creation desc"
    )
    
    return requests
