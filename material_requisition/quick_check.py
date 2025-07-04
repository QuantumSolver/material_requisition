import frappe

def quick_pmep_check():
    """
    Quick PMEP deployment verification
    Use: bench execute material_requisition.quick_check.quick_pmep_check
    """
    print("🚀 PMEP Quick Deployment Check")
    print("=" * 50)
    
    checks = []
    
    # 1. Homepage Check
    try:
        website_settings = frappe.get_single("Website Settings")
        if website_settings.home_page == "home":
            checks.append("✅ Homepage: PMEP interface configured")
        else:
            checks.append(f"❌ Homepage: Shows '{website_settings.home_page}' instead of PMEP")
    except Exception as e:
        checks.append(f"❌ Homepage: Error - {str(e)}")
    
    # 2. Purchase Receipt API Check
    try:
        from material_requisition.api.purchase_receipt import get_purchase_receipts
        checks.append("✅ Purchase Receipt: API accessible")
    except ImportError:
        checks.append("❌ Purchase Receipt: API not found")
    except Exception as e:
        checks.append(f"⚠️ Purchase Receipt: API warning - {str(e)}")
    
    # 3. Vue Components Check
    import os
    app_path = frappe.get_app_path("material_requisition")
    app_root = os.path.dirname(app_path)  # Get app root directory
    receipt_components = [
        "Promep/src/views/ReceiptDetail.vue",
        "Promep/src/views/ReceiptsList.vue"
    ]

    vue_found = 0
    for component in receipt_components:
        if os.path.exists(os.path.join(app_root, component)):
            vue_found += 1
    
    if vue_found == len(receipt_components):
        checks.append("✅ Vue Components: All Purchase Receipt components found")
    else:
        checks.append(f"❌ Vue Components: {vue_found}/{len(receipt_components)} found")
    
    # 4. DocType Check
    try:
        if frappe.db.exists("DocType", "Purchase Receipt"):
            checks.append("✅ Database: Purchase Receipt doctype available")
        else:
            checks.append("❌ Database: Purchase Receipt doctype missing")
    except Exception as e:
        checks.append(f"❌ Database: Error - {str(e)}")
    
    # 5. Template Check
    templates_path = os.path.join(app_path, "templates", "pages")
    if os.path.exists(os.path.join(templates_path, "home.html")):
        checks.append("✅ Templates: PMEP homepage template found")
    else:
        checks.append("❌ Templates: PMEP homepage template missing")
    
    # Print Results
    print("\n📋 QUICK CHECK RESULTS:")
    for check in checks:
        print(f"  {check}")
    
    # Summary
    passed = len([c for c in checks if c.startswith("✅")])
    total = len(checks)
    
    print(f"\n📊 SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 PMEP DEPLOYMENT LOOKS GOOD!")
        print("💡 Next steps:")
        print("   1. Visit your homepage - should show PMEP interface")
        print("   2. Login and check Purchase Receipts are available")
        print("   3. Test the complete workflow: Material Request → Purchase Order → Purchase Receipt")
    else:
        print("🔧 PMEP DEPLOYMENT NEEDS ATTENTION")
        print("💡 Run full validation: bench execute material_requisition.validation.run_validation")
        print("💡 Or check the PMEP_CHECKLIST.md for detailed troubleshooting")
    
    print("=" * 50)
    
    return {
        "passed": passed,
        "total": total,
        "success_rate": (passed/total*100) if total > 0 else 0,
        "checks": checks
    }
