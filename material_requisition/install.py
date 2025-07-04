import frappe
from frappe import _
import os
import subprocess

def after_install():
    """
    Automatically configure PMEP after installation
    """
    try:
        print("🚀 Starting PMEP post-installation setup...")
        
        # 1. Setup PMEP theme and homepage
        setup_pmep_theme_and_homepage()
        
        # 2. Build assets to ensure all files are properly compiled
        build_assets()
        
        # 3. Clear cache to ensure fresh start
        clear_all_caches()
        
        # 4. Setup website settings
        setup_website_settings()
        
        print("✅ PMEP installation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during PMEP installation: {str(e)}")
        frappe.log_error(f"PMEP Installation Error: {str(e)}", "PMEP Installation")

def setup_pmep_theme_and_homepage():
    """Setup PMEP theme and configure homepage"""
    try:
        # Import and run the banner setup
        from material_requisition.setup.banner_setup import setup_pmep_theme
        setup_pmep_theme()
        print("✅ PMEP theme configured")
        
    except Exception as e:
        print(f"❌ Error setting up PMEP theme: {str(e)}")
        frappe.log_error(f"PMEP Theme Setup Error: {str(e)}", "PMEP Installation")

def build_assets():
    """Build assets to ensure all files are compiled"""
    try:
        # Get the bench path
        bench_path = frappe.utils.get_bench_path()
        
        # Build assets for material_requisition app
        cmd = f"cd {bench_path} && bench build --app material_requisition"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Assets built successfully")
        else:
            print(f"⚠️ Asset build warning: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error building assets: {str(e)}")
        # Don't fail installation for asset build issues
        pass

def clear_all_caches():
    """Clear all caches"""
    try:
        frappe.clear_cache()
        # Use the correct method for clearing website cache
        from frappe.website.utils import clear_cache as clear_website_cache
        clear_website_cache()
        print("✅ Caches cleared")

    except Exception as e:
        print(f"❌ Error clearing caches: {str(e)}")

def setup_website_settings():
    """Configure website settings for PMEP"""
    try:
        # Set homepage to our custom page
        website_settings = frappe.get_single("Website Settings")
        
        # Configure homepage
        website_settings.home_page = "home"
        website_settings.title_prefix = "PMEP - "
        
        # Save settings
        website_settings.save()
        
        print("✅ Website settings configured")
        
    except Exception as e:
        print(f"❌ Error configuring website settings: {str(e)}")
        frappe.log_error(f"Website Settings Error: {str(e)}", "PMEP Installation")

def before_uninstall():
    """Cleanup before uninstalling PMEP"""
    try:
        print("🧹 Cleaning up PMEP configuration...")
        
        # Reset website settings to default
        website_settings = frappe.get_single("Website Settings")
        website_settings.home_page = ""
        website_settings.title_prefix = ""
        website_settings.save()
        
        # Clear caches
        frappe.clear_cache()
        frappe.clear_website_cache()
        
        print("✅ PMEP cleanup completed")
        
    except Exception as e:
        print(f"❌ Error during PMEP cleanup: {str(e)}")
        frappe.log_error(f"PMEP Cleanup Error: {str(e)}", "PMEP Uninstall")
