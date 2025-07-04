import frappe

def setup_pmep_banner_theme():
    """
    Setup PMEP banner theme and remove old banner from website settings
    """
    try:
        # Get current website settings
        website_settings = frappe.get_single("Website Settings")

        # Store the old banner HTML for reference (optional)
        old_banner = website_settings.get("banner_html", "")
        if old_banner:
            frappe.log_error(f"Old banner HTML removed: {old_banner}", "PMEP Banner Setup")

        # Clear the old banner HTML
        website_settings.banner_html = ""

        # Update website settings for PMEP theme
        website_settings.app_name = "PMEP"
        website_settings.title_prefix = "PMEP"

        # Set custom favicon if available
        website_settings.favicon = "/assets/material_requisition/images/favicon.ico"

        # Save the changes
        website_settings.save()

        frappe.db.commit()

        print("✅ PMEP Banner Theme setup completed successfully!")
        print("✅ Old banner HTML removed from Website Settings")
        print("✅ Website settings updated with PMEP branding")

        return True

    except Exception as e:
        frappe.log_error(f"PMEP Banner Setup Error: {str(e)}")
        print(f"❌ Error setting up PMEP banner theme: {str(e)}")
        return False

def setup_pmep_theme():
    """
    Setup PMEP integrated theme (replaces banner approach)
    """
    try:
        # Ensure we're in a valid Frappe context
        if not frappe.db:
            print("⚠️ No database connection available, skipping theme setup")
            return False

        # Get website settings
        website_settings = frappe.get_single("Website Settings")

        # Update website settings for PMEP theme
        website_settings.app_name = "PMEP"
        website_settings.title_prefix = "PMEP - "

        # Set the homepage to display our custom home page
        website_settings.home_page = "home"

        # Set default redirect after login to Promep
        website_settings.role_based_sidebar = 0

        # Set custom favicon if available
        website_settings.favicon = "/assets/material_requisition/images/favicon.ico"

        # Add PMEP theme CSS to website settings
        custom_css = """
/* PMEP Theme Integration */
@import url('/assets/material_requisition/css/pmep_theme.css');

/* Additional website-specific styling */
.navbar-brand::before {
    content: 'Pro-Mep';
    display: inline-block;
    font-family: 'Montserrat', Arial, sans-serif;
    font-weight: 700;
    font-size: 18px;
    background: linear-gradient(-45deg, #1e293b, #374151, #4b5563, #1f2937);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-right: 8px;
    vertical-align: middle;
    letter-spacing: -0.01em;
    animation: navGradientShift 6s ease-in-out infinite;
}

@keyframes navGradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
"""

        website_settings.custom_css = custom_css

        # Save the changes
        website_settings.save()
        frappe.db.commit()

        # Clear website cache to apply changes immediately
        from frappe.website.utils import clear_cache as clear_website_cache
        clear_website_cache()
        frappe.clear_cache()

        print("✅ PMEP Integrated Theme setup completed successfully!")
        print("✅ Website settings updated with PMEP branding")
        print("✅ Custom CSS applied for theme integration")
        print("✅ Homepage set to display on root URL (/)")

        return True

    except Exception as e:
        frappe.log_error(f"PMEP Theme Setup Error: {str(e)}")
        print(f"❌ Error setting up PMEP theme: {str(e)}")
        return False

def remove_old_banner():
    """
    Remove old banner HTML from website settings
    """
    try:
        # Get website settings
        website_settings = frappe.get_single("Website Settings")

        # Store old banner for reference
        old_banner = website_settings.get("banner_html", "")
        if old_banner:
            print(f"📝 Removed content: {old_banner[:100]}...")

        # Clear the banner HTML
        website_settings.banner_html = ""

        # Save the changes
        website_settings.save()
        frappe.db.commit()

        print("✅ Old banner HTML removed successfully")
        return True

    except Exception as e:
        frappe.log_error(f"Remove Banner Error: {str(e)}")
        print(f"❌ Error removing old banner: {str(e)}")
        return False

def remove_old_banner():
    """
    Remove the old banner HTML from website settings
    """
    try:
        website_settings = frappe.get_single("Website Settings")
        
        if website_settings.banner_html:
            old_banner = website_settings.banner_html
            website_settings.banner_html = ""
            website_settings.save()
            frappe.db.commit()
            
            print("✅ Old banner HTML removed successfully")
            print(f"📝 Removed content: {old_banner[:100]}...")
            return True
        else:
            print("ℹ️ No banner HTML found in website settings")
            return True
            
    except Exception as e:
        print(f"❌ Error removing old banner: {str(e)}")
        return False

def verify_banner_setup():
    """
    Verify that the banner setup is working correctly
    """
    try:
        # Check if templates exist
        template_path = frappe.get_app_path("material_requisition", "templates", "includes", "banner.html")
        if not frappe.os.path.exists(template_path):
            print("❌ Banner template not found")
            return False
        
        # Check if assets directory exists
        assets_path = frappe.get_app_path("material_requisition", "public", "images")
        if not frappe.os.path.exists(assets_path):
            print("❌ Assets directory not found")
            return False
        
        # Check website settings
        website_settings = frappe.get_single("Website Settings")
        if website_settings.banner_html:
            print("⚠️ Warning: Old banner HTML still exists in website settings")
            return False
        
        print("✅ Banner setup verification passed")
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False

def install_pmep_theme():
    """
    Complete installation of PMEP theme
    """
    print("🚀 Installing PMEP Banner Theme...")
    print("=" * 50)
    
    # Step 1: Remove old banner
    print("Step 1: Removing old banner from website settings...")
    if remove_old_banner():
        print("✅ Step 1 completed")
    else:
        print("❌ Step 1 failed")
        return False
    
    # Step 2: Setup new theme
    print("\nStep 2: Setting up PMEP banner theme...")
    if setup_pmep_banner_theme():
        print("✅ Step 2 completed")
    else:
        print("❌ Step 2 failed")
        return False
    
    # Step 3: Verify installation
    print("\nStep 3: Verifying installation...")
    if verify_banner_setup():
        print("✅ Step 3 completed")
    else:
        print("❌ Step 3 failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 PMEP Banner Theme installation completed successfully!")
    print("\nNext steps:")
    print("1. Copy your logo file to: apps/material_requisition/material_requisition/public/images/pro-mep-logo.png")
    print("2. Run: bench build --app material_requisition")
    print("3. Restart your server: bench restart")
    print("4. Visit your website to see the new banner")
    
    return True

def uninstall_pmep_theme():
    """
    Uninstall PMEP theme and restore defaults
    """
    try:
        website_settings = frappe.get_single("Website Settings")
        
        # Reset website settings
        website_settings.app_name = ""
        website_settings.title_prefix = ""
        website_settings.favicon = ""
        
        website_settings.save()
        frappe.db.commit()
        
        print("✅ PMEP theme uninstalled successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error uninstalling theme: {str(e)}")
        return False

# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "install":
            install_pmep_theme()
        elif command == "uninstall":
            uninstall_pmep_theme()
        elif command == "verify":
            verify_banner_setup()
        elif command == "remove-old":
            remove_old_banner()
        else:
            print("Usage: python banner_setup.py [install|uninstall|verify|remove-old]")
    else:
        install_pmep_theme()
