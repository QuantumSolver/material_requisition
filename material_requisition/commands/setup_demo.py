import click
import frappe
from frappe.commands import pass_context

@click.command('setup-material-requisition-demo')
@pass_context
def setup_demo(context):
    """Setup demo data for Material Requisition System"""
    
    site = context.sites[0] if context.sites else None
    if not site:
        click.echo("Please specify a site")
        return
    
    frappe.init(site=site)
    frappe.connect()
    
    try:
        from material_requisition.fixtures.sample_items import create_sample_items, create_sample_suppliers
        
        click.echo("Creating sample items...")
        create_sample_items()
        
        click.echo("Creating sample suppliers...")
        create_sample_suppliers()
        
        frappe.db.commit()
        click.echo("Demo data setup completed successfully!")
        
    except Exception as e:
        frappe.db.rollback()
        click.echo(f"Error setting up demo data: {str(e)}")
        raise
    finally:
        frappe.destroy()

commands = [setup_demo]
