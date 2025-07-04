import frappe
import os
from frappe.utils import get_bench_path

def validate_pmep_installation():
    """
    Comprehensive validation script for PMEP installation
    Returns a detailed checklist of what's working and what needs attention
    """
    print("🔍 PMEP Installation Validation Starting...")
    print("=" * 60)
    
    validation_results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }
    
    # 1. Check core files
    validate_core_files(validation_results)
    
    # 2. Check API endpoints
    validate_api_endpoints(validation_results)
    
    # 3. Check templates
    validate_templates(validation_results)
    
    # 4. Check assets
    validate_assets(validation_results)
    
    # 5. Check Vue components
    validate_vue_components(validation_results)
    
    # 6. Check website settings
    validate_website_settings(validation_results)
    
    # 7. Check database setup
    validate_database_setup(validation_results)
    
    # Print results
    print_validation_results(validation_results)
    
    return validation_results

def validate_core_files(results):
    """Validate core PMEP files exist"""
    print("📁 Checking Core Files...")
    
    app_path = frappe.get_app_path("material_requisition")
    
    core_files = [
        "hooks.py",
        "install.py", 
        "build_hooks.py",
        "setup/banner_setup.py",
        "api/purchase_receipt.py",
        "public/js/purchase_receipt.js",
        "public/css/pmep_theme.css"
    ]
    
    for file_path in core_files:
        full_path = os.path.join(app_path, file_path)
        if os.path.exists(full_path):
            results["passed"].append(f"✅ Core file exists: {file_path}")
        else:
            results["failed"].append(f"❌ Missing core file: {file_path}")

def validate_api_endpoints(results):
    """Validate API endpoints are accessible"""
    print("🔌 Checking API Endpoints...")
    
    try:
        # Check if purchase receipt API is accessible
        from material_requisition.api.purchase_receipt import get_purchase_receipts
        results["passed"].append("✅ Purchase Receipt API accessible")
    except ImportError as e:
        results["failed"].append(f"❌ Purchase Receipt API not accessible: {str(e)}")
    except Exception as e:
        results["warnings"].append(f"⚠️ Purchase Receipt API warning: {str(e)}")

def validate_templates(results):
    """Validate template files"""
    print("📄 Checking Templates...")
    
    app_path = frappe.get_app_path("material_requisition")
    templates_path = os.path.join(app_path, "templates", "pages")
    
    required_templates = [
        "home.html",
        "login.html", 
        "index.html"
    ]
    
    for template in required_templates:
        template_path = os.path.join(templates_path, template)
        if os.path.exists(template_path):
            # Check if template has Pro-Mep logo
            with open(template_path, 'r') as f:
                content = f.read()
                if "Pro-Mep" in content:
                    results["passed"].append(f"✅ Template with logo: {template}")
                else:
                    results["warnings"].append(f"⚠️ Template missing logo: {template}")
        else:
            results["failed"].append(f"❌ Missing template: {template}")

def validate_assets(results):
    """Validate asset files"""
    print("🎨 Checking Assets...")
    
    app_path = frappe.get_app_path("material_requisition")
    
    # Check CSS files
    css_path = os.path.join(app_path, "public", "css", "pmep_theme.css")
    if os.path.exists(css_path):
        results["passed"].append("✅ PMEP theme CSS exists")
    else:
        results["failed"].append("❌ Missing PMEP theme CSS")
    
    # Check JS files
    js_files = [
        "public/js/material_request.js",
        "public/js/purchase_order.js", 
        "public/js/purchase_receipt.js"
    ]
    
    for js_file in js_files:
        js_path = os.path.join(app_path, js_file)
        if os.path.exists(js_path):
            results["passed"].append(f"✅ JS file exists: {js_file}")
        else:
            results["failed"].append(f"❌ Missing JS file: {js_file}")

def validate_vue_components(results):
    """Validate Vue.js components"""
    print("⚡ Checking Vue Components...")
    
    app_path = frappe.get_app_path("material_requisition")
    vue_components = [
        "Promep/src/views/ReceiptDetail.vue",
        "Promep/src/views/ReceiptsList.vue"
    ]
    
    for component in vue_components:
        component_path = os.path.join(app_path, component)
        if os.path.exists(component_path):
            results["passed"].append(f"✅ Vue component exists: {component}")
        else:
            results["failed"].append(f"❌ Missing Vue component: {component}")

def validate_website_settings(results):
    """Validate website settings configuration"""
    print("⚙️ Checking Website Settings...")
    
    try:
        website_settings = frappe.get_single("Website Settings")
        
        # Check homepage
        if website_settings.home_page == "home":
            results["passed"].append("✅ Homepage set to PMEP")
        else:
            results["failed"].append(f"❌ Homepage not set correctly: {website_settings.home_page}")
        
        # Check app name
        if "PMEP" in (website_settings.app_name or ""):
            results["passed"].append("✅ App name contains PMEP")
        else:
            results["warnings"].append("⚠️ App name doesn't contain PMEP")
            
        # Check custom CSS
        if website_settings.custom_css and "Pro-Mep" in website_settings.custom_css:
            results["passed"].append("✅ Custom CSS includes Pro-Mep styling")
        else:
            results["warnings"].append("⚠️ Custom CSS may be missing Pro-Mep styling")
            
    except Exception as e:
        results["failed"].append(f"❌ Website settings error: {str(e)}")

def validate_database_setup(results):
    """Validate database configuration"""
    print("🗄️ Checking Database Setup...")
    
    try:
        # Check if Purchase Receipt doctype is accessible
        if frappe.db.exists("DocType", "Purchase Receipt"):
            results["passed"].append("✅ Purchase Receipt doctype exists")
        else:
            results["failed"].append("❌ Purchase Receipt doctype not found")
            
        # Check if Material Request doctype is accessible  
        if frappe.db.exists("DocType", "Material Request"):
            results["passed"].append("✅ Material Request doctype exists")
        else:
            results["failed"].append("❌ Material Request doctype not found")
            
    except Exception as e:
        results["failed"].append(f"❌ Database validation error: {str(e)}")

def print_validation_results(results):
    """Print formatted validation results"""
    print("\n" + "=" * 60)
    print("📊 PMEP VALIDATION RESULTS")
    print("=" * 60)
    
    print(f"\n✅ PASSED ({len(results['passed'])} items):")
    for item in results["passed"]:
        print(f"  {item}")
    
    if results["warnings"]:
        print(f"\n⚠️ WARNINGS ({len(results['warnings'])} items):")
        for item in results["warnings"]:
            print(f"  {item}")
    
    if results["failed"]:
        print(f"\n❌ FAILED ({len(results['failed'])} items):")
        for item in results["failed"]:
            print(f"  {item}")
    
    print("\n" + "=" * 60)
    
    total_checks = len(results["passed"]) + len(results["warnings"]) + len(results["failed"])
    success_rate = (len(results["passed"]) / total_checks * 100) if total_checks > 0 else 0
    
    print(f"📈 SUCCESS RATE: {success_rate:.1f}% ({len(results['passed'])}/{total_checks})")
    
    if len(results["failed"]) == 0:
        print("🎉 PMEP INSTALLATION IS HEALTHY!")
    else:
        print("🔧 PMEP INSTALLATION NEEDS ATTENTION")
    
    print("=" * 60)

def run_validation():
    """Entry point for validation"""
    return validate_pmep_installation()
