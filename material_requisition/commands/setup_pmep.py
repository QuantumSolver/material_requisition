import click
import frappe
from frappe.commands import pass_context

@click.command('setup-pmep')
@pass_context
def setup_pmep(context):
    """
    Setup PMEP theme and configuration
    Usage: bench execute material_requisition.commands.setup_pmep.setup_pmep
    """
    try:
        print("🚀 Setting up PMEP theme and configuration...")
        
        # Import and run setup functions
        from material_requisition.setup.banner_setup import setup_pmep_theme
        from material_requisition.install import build_assets, clear_all_caches
        
        # Setup theme
        if setup_pmep_theme():
            print("✅ PMEP theme configured successfully")
        else:
            print("❌ Failed to configure PMEP theme")
            return
            
        # Build assets
        print("🔧 Building assets...")
        build_assets()
        
        # Clear caches
        print("🧹 Clearing caches...")
        clear_all_caches()
        
        print("🎉 PMEP setup completed successfully!")
        print("📝 Your homepage should now display the PMEP interface")
        print("🔗 Visit your site to see the changes")
        
    except Exception as e:
        print(f"❌ Error during PMEP setup: {str(e)}")
        frappe.log_error(f"PMEP Setup Command Error: {str(e)}", "PMEP Setup")

def setup_pmep_command():
    """Function to be called directly"""
    setup_pmep.main(standalone_mode=False)
