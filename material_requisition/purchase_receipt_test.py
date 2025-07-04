import frappe

def test_purchase_receipt_functionality():
    """
    Test Purchase Receipt functionality to ensure it's working
    Use: bench execute material_requisition.purchase_receipt_test.test_purchase_receipt_functionality
    """
    print("🧪 Testing Purchase Receipt Functionality")
    print("=" * 50)
    
    results = []
    
    # 1. Test API Import
    try:
        from material_requisition.api.purchase_receipt import get_purchase_receipts, get_receipt_detail
        results.append("✅ Purchase Receipt API imports successfully")
    except ImportError as e:
        results.append(f"❌ Purchase Receipt API import failed: {str(e)}")
        return results
    
    # 2. Test API Functionality
    try:
        receipts = get_purchase_receipts()
        if receipts and 'receipts' in receipts:
            count = len(receipts['receipts'])
            results.append(f"✅ Purchase Receipt API returns {count} receipts")
        else:
            results.append("⚠️ Purchase Receipt API returns empty result")
    except Exception as e:
        results.append(f"❌ Purchase Receipt API error: {str(e)}")
    
    # 3. Test DocType Access
    try:
        if frappe.db.exists("DocType", "Purchase Receipt"):
            results.append("✅ Purchase Receipt DocType is accessible")
        else:
            results.append("❌ Purchase Receipt DocType not found")
    except Exception as e:
        results.append(f"❌ DocType check error: {str(e)}")
    
    # 4. Test Vue Components
    import os
    app_path = frappe.get_app_path("material_requisition")
    app_root = os.path.dirname(app_path)  # Get app root directory

    vue_components = [
        "Promep/src/views/ReceiptsList.vue",
        "Promep/src/views/ReceiptDetail.vue"
    ]

    for component in vue_components:
        component_path = os.path.join(app_root, component)
        if os.path.exists(component_path):
            results.append(f"✅ Vue component exists: {component}")
        else:
            results.append(f"❌ Vue component missing: {component}")
    
    # 5. Test Built Assets
    built_assets = [
        "public/Promep/assets/ReceiptsList-DTWaDWwk.js",
        "public/Promep/assets/ReceiptDetail-DhPwCX1E.js"
    ]

    for asset in built_assets:
        asset_path = os.path.join(app_path, asset)
        if os.path.exists(asset_path):
            results.append(f"✅ Built asset exists: {os.path.basename(asset)}")
        else:
            results.append(f"❌ Built asset missing: {os.path.basename(asset)}")
    
    # 6. Test JavaScript Integration
    js_file = os.path.join(app_path, "public/js/purchase_receipt.js")
    if os.path.exists(js_file):
        results.append("✅ Purchase Receipt JavaScript integration exists")
    else:
        results.append("❌ Purchase Receipt JavaScript integration missing")
    
    # Print Results
    print("\n📋 TEST RESULTS:")
    for result in results:
        print(f"  {result}")
    
    # Summary
    passed = len([r for r in results if r.startswith("✅")])
    total = len(results)
    
    print(f"\n📊 SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 PURCHASE RECEIPT FUNCTIONALITY IS WORKING!")
        print("💡 If you can't see the button, make sure you're logged in to access /promep")
    else:
        print("🔧 PURCHASE RECEIPT FUNCTIONALITY NEEDS ATTENTION")
    
    print("=" * 50)
    
    return results

def check_purchase_receipt_in_promep():
    """Check if Purchase Receipt is properly integrated in Promep interface"""
    print("🔍 Checking Purchase Receipt Integration in Promep")
    print("=" * 50)

    import os
    app_path = frappe.get_app_path("material_requisition")
    app_root = os.path.dirname(app_path)  # Get app root directory

    # Check Home.vue for Purchase Receipt button
    home_vue_path = os.path.join(app_root, "Promep/src/views/Home.vue")
    if os.path.exists(home_vue_path):
        with open(home_vue_path, 'r') as f:
            content = f.read()
            if "Purchase Receipts" in content and "viewReceipts" in content:
                print("✅ Purchase Receipt button found in Home.vue")
            else:
                print("❌ Purchase Receipt button missing from Home.vue")
    else:
        print("❌ Home.vue file not found")

    # Check router for Receipt routes
    router_path = os.path.join(app_root, "Promep/src/router/index.js")
    if os.path.exists(router_path):
        with open(router_path, 'r') as f:
            content = f.read()
            if "/receipts" in content and "ReceiptsList" in content:
                print("✅ Purchase Receipt routes found in router")
            else:
                print("❌ Purchase Receipt routes missing from router")
    else:
        print("❌ Router file not found")

    print("=" * 50)

def run_all_tests():
    """Run all Purchase Receipt tests"""
    test_purchase_receipt_functionality()
    print("\n")
    check_purchase_receipt_in_promep()
