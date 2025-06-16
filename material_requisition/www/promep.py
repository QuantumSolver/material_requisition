import frappe

def get_context(context):
    """Context for the Material Requisition SPA"""

    # Debug logging
    frappe.logger().info(f"promep.py: User is {frappe.session.user}")

    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.logger().info("promep.py: Redirecting guest user to login")
        frappe.local.flags.redirect_location = "/login?redirect-to=/promep"
        raise frappe.Redirect

    frappe.logger().info("promep.py: User is authenticated, serving page")

    context.no_cache = 1
    context.show_sidebar = False

    # Add some debug info to context
    context.debug_user = frappe.session.user
    context.debug_csrf = frappe.session.csrf_token

    return context
