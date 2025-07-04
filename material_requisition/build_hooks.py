import frappe
import os
import subprocess
from frappe.utils import get_bench_path

def after_build():
    """
    Hook that runs after building assets
    Ensures PMEP theme and configuration are properly applied
    """
    try:
        print("🔧 Running PMEP post-build setup...")
        
        # Apply PMEP theme configuration
        apply_pmep_configuration()
        
        # Clear website cache to ensure fresh assets
        frappe.clear_website_cache()
        
        print("✅ PMEP post-build setup completed")
        
    except Exception as e:
        print(f"❌ Error in PMEP post-build setup: {str(e)}")
        frappe.log_error(f"PMEP Build Hook Error: {str(e)}", "PMEP Build")

def apply_pmep_configuration():
    """Apply PMEP theme and configuration"""
    try:
        # Import and run the banner setup
        from material_requisition.setup.banner_setup import setup_pmep_theme
        setup_pmep_theme()
        
        # Ensure website settings are configured
        configure_website_settings()
        
        print("✅ PMEP configuration applied")
        
    except Exception as e:
        print(f"❌ Error applying PMEP configuration: {str(e)}")
        frappe.log_error(f"PMEP Configuration Error: {str(e)}", "PMEP Build")

def configure_website_settings():
    """Configure website settings for PMEP"""
    try:
        if frappe.db.exists("Website Settings", "Website Settings"):
            website_settings = frappe.get_single("Website Settings")
            
            # Set homepage if not already set
            if not website_settings.home_page or website_settings.home_page == "login":
                website_settings.home_page = "home"
                
            # Set title prefix
            if not website_settings.title_prefix or "PMEP" not in website_settings.title_prefix:
                website_settings.title_prefix = "PMEP - "
                
            website_settings.save()
            
    except Exception as e:
        print(f"❌ Error configuring website settings: {str(e)}")

def before_build():
    """
    Hook that runs before building assets
    Ensures all necessary files are in place
    """
    try:
        print("🔧 Running PMEP pre-build setup...")
        
        # Ensure all template files exist
        ensure_template_files()
        
        print("✅ PMEP pre-build setup completed")
        
    except Exception as e:
        print(f"❌ Error in PMEP pre-build setup: {str(e)}")
        frappe.log_error(f"PMEP Pre-Build Error: {str(e)}", "PMEP Build")

def ensure_template_files():
    """Ensure all required template files exist"""
    try:
        app_path = frappe.get_app_path("material_requisition")
        templates_path = os.path.join(app_path, "templates", "pages")
        
        required_templates = ["home.html", "login.html", "index.html"]
        
        for template in required_templates:
            template_path = os.path.join(templates_path, template)
            if not os.path.exists(template_path):
                print(f"⚠️ Missing template: {template}")
            else:
                print(f"✅ Template found: {template}")
                
    except Exception as e:
        print(f"❌ Error checking template files: {str(e)}")
