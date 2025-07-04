import frappe
import os
import glob
from frappe.utils import get_site_path

@frappe.whitelist(allow_guest=True)
def get_latest_promep_assets():
    """
    Auto-detect the latest Promep assets for dynamic loading
    Returns the latest JS and CSS files for the Promep Vue application
    """
    try:
        # Get the assets directory path from the app's public directory
        app_path = frappe.get_app_path("material_requisition")
        assets_path = os.path.join(app_path, "public", "Promep", "assets")

        if not os.path.exists(assets_path):
            # Fallback: try the site's public directory
            site_path = get_site_path()
            assets_path = os.path.join(site_path, "public", "assets", "material_requisition", "Promep", "assets")

            if not os.path.exists(assets_path):
                return {
                    "js": [],
                    "css": [],
                    "error": f"Promep assets directory not found in {assets_path}"
                }
        
        # Find all JS and CSS files
        js_files = []
        css_files = []
        
        # Look for index files (main entry points)
        index_js_pattern = os.path.join(assets_path, "index-*.js")
        index_css_pattern = os.path.join(assets_path, "index-*.css")
        
        # Get the latest index files
        js_matches = glob.glob(index_js_pattern)
        css_matches = glob.glob(index_css_pattern)
        
        # Sort by modification time to get the latest
        if js_matches:
            latest_js = max(js_matches, key=os.path.getmtime)
            js_filename = os.path.basename(latest_js)
            js_files.append(f"/assets/material_requisition/Promep/assets/{js_filename}")
        
        if css_matches:
            latest_css = max(css_matches, key=os.path.getmtime)
            css_filename = os.path.basename(latest_css)
            css_files.append(f"/assets/material_requisition/Promep/assets/{css_filename}")
        
        # If no index files found, look for any JS/CSS files
        if not js_files:
            all_js = glob.glob(os.path.join(assets_path, "*.js"))
            if all_js:
                latest_js = max(all_js, key=os.path.getmtime)
                js_filename = os.path.basename(latest_js)
                js_files.append(f"/assets/material_requisition/Promep/assets/{js_filename}")
        
        if not css_files:
            all_css = glob.glob(os.path.join(assets_path, "*.css"))
            if all_css:
                latest_css = max(all_css, key=os.path.getmtime)
                css_filename = os.path.basename(latest_css)
                css_files.append(f"/assets/material_requisition/Promep/assets/{css_filename}")
        
        return {
            "js": js_files,
            "css": css_files,
            "timestamp": frappe.utils.now(),
            "assets_found": len(js_files) + len(css_files)
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting Promep assets: {str(e)}", "Promep Assets")
        return {
            "js": [],
            "css": [],
            "error": str(e)
        }

def get_promep_assets():
    """
    Template function to get Promep assets for Jinja templates
    """
    try:
        result = get_latest_promep_assets()
        if result.get("error"):
            return None
        return result
    except:
        return None

@frappe.whitelist()
def rebuild_promep_assets():
    """
    Trigger a rebuild of Promep assets
    """
    try:
        import subprocess
        import frappe.utils
        
        bench_path = frappe.utils.get_bench_path()
        
        # Build the Promep Vue application
        cmd = f"cd {bench_path} && bench build --app material_requisition"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Promep assets rebuilt successfully",
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "message": "Failed to rebuild Promep assets",
                "error": result.stderr
            }
            
    except Exception as e:
        frappe.log_error(f"Error rebuilding Promep assets: {str(e)}", "Promep Assets")
        return {
            "success": False,
            "message": "Error rebuilding assets",
            "error": str(e)
        }

@frappe.whitelist()
def get_asset_info():
    """
    Get detailed information about current Promep assets
    """
    try:
        site_path = get_site_path()
        assets_path = os.path.join(site_path, "public", "assets", "material_requisition", "Promep", "assets")
        
        if not os.path.exists(assets_path):
            return {"error": "Assets directory not found"}
        
        files = []
        for file in os.listdir(assets_path):
            if file.endswith(('.js', '.css')):
                file_path = os.path.join(assets_path, file)
                stat = os.stat(file_path)
                files.append({
                    "name": file,
                    "size": stat.st_size,
                    "modified": frappe.utils.formatdate(frappe.utils.datetime.datetime.fromtimestamp(stat.st_mtime)),
                    "url": f"/assets/material_requisition/Promep/assets/{file}"
                })
        
        return {
            "files": sorted(files, key=lambda x: x["name"]),
            "total_files": len(files),
            "directory": assets_path
        }
        
    except Exception as e:
        return {"error": str(e)}
