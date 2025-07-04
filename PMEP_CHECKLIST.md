# PMEP Installation & Validation Checklist

## 🚀 Pre-Installation Checklist

- [ ] Frappe/ERPNext environment is properly set up
- [ ] Bench is running and accessible
- [ ] Database connection is working
- [ ] Git access to the repository is available

## 📦 Installation Steps

### 1. Get the App
```bash
bench get-app https://github.com/QuantumSolver/material_requisition.git
```
- [ ] App downloaded successfully
- [ ] No git errors during download

### 2. Install the App
```bash
bench install-app material_requisition
```
- [ ] Installation completed without errors
- [ ] Automatic setup scripts ran successfully
- [ ] No database migration errors

### 3. Build Assets
```bash
bench build --app material_requisition
```
- [ ] Assets built successfully
- [ ] No compilation errors
- [ ] Validation checklist passed

## ✅ Post-Installation Validation

### Core Functionality
- [ ] **Homepage**: Visit `/` - should show PMEP interface (not default Frappe)
- [ ] **Login Page**: Visit `/login` - should show Pro-Mep animated logo
- [ ] **Navigation**: Pro-Mep logo visible in navbar with animation

### Material Management
- [ ] **Material Request**: Available in ERPNext menu
- [ ] **Purchase Order**: Available in ERPNext menu  
- [ ] **Purchase Receipt**: Available in ERPNext menu ⚠️ (This was missing!)

### Promep Interface
- [ ] **Promep Access**: Visit `/promep` - Vue.js interface loads
- [ ] **Material Requests**: List and detail views work
- [ ] **Purchase Orders**: List and detail views work
- [ ] **Purchase Receipts**: List and detail views work ⚠️ (Check this!)

### API Endpoints
- [ ] **Material Request API**: `/api/method/material_requisition.api.material_request.*`
- [ ] **Purchase Order API**: `/api/method/material_requisition.api.purchase_order.*`
- [ ] **Purchase Receipt API**: `/api/method/material_requisition.api.purchase_receipt.*` ⚠️

### Assets & Styling
- [ ] **PMEP Theme CSS**: Loads properly
- [ ] **Animated Logo**: Gradient animation works
- [ ] **Responsive Design**: Works on mobile and desktop
- [ ] **Custom Styling**: PMEP branding applied throughout

## 🔧 Manual Validation Commands

### Run Full Validation
```bash
bench execute material_requisition.validation.run_validation
```

### Manual Setup (if needed)
```bash
# Run installation setup
bench execute material_requisition.install.after_install

# Setup theme manually
bench execute material_requisition.setup.banner_setup.setup_pmep_theme

# Clear caches
bench clear-cache
bench clear-website-cache
```

### Check Specific Components
```bash
# Check if Purchase Receipt API works
bench execute "import frappe; from material_requisition.api.purchase_receipt import get_purchase_receipts; print('Purchase Receipt API OK')"

# Check website settings
bench execute "import frappe; ws = frappe.get_single('Website Settings'); print(f'Homepage: {ws.home_page}, App: {ws.app_name}')"
```

## 🚨 Common Issues & Fixes

### Issue: Default Frappe Homepage Shows
**Fix:**
```bash
bench execute material_requisition.setup.banner_setup.setup_pmep_theme
bench clear-website-cache
```

### Issue: Purchase Receipts Missing
**Fix:**
```bash
# Ensure files are present
ls apps/material_requisition/material_requisition/api/purchase_receipt.py
ls apps/material_requisition/Promep/src/views/Receipt*.vue

# Rebuild if missing
bench build --app material_requisition
```

### Issue: Assets Not Loading
**Fix:**
```bash
bench build --app material_requisition
bench clear-cache
bench restart
```

### Issue: Logo Not Animated
**Fix:**
```bash
# Check if CSS is loaded
curl -I http://your-site/assets/material_requisition/css/pmep_theme.css

# Rebuild if needed
bench build --app material_requisition
```

## 📊 Success Criteria

### ✅ Installation Successful When:
- [ ] Homepage shows PMEP interface (not default Frappe)
- [ ] All three modules work: Material Request, Purchase Order, **Purchase Receipt**
- [ ] Promep Vue.js interface loads and functions
- [ ] Animated Pro-Mep logo displays correctly
- [ ] All API endpoints respond correctly
- [ ] No console errors in browser
- [ ] Validation script shows >90% success rate

### 🎯 Key Features Working:
- [ ] **End-to-End Workflow**: Material Request → Purchase Order → Purchase Receipt
- [ ] **Bidirectional Navigation**: ERPNext ↔ Promep interface
- [ ] **Professional Branding**: Animated logo and PMEP theme
- [ ] **Responsive Design**: Works on all devices
- [ ] **Production Ready**: No manual configuration required

## 🔍 Validation Script Output

The validation script should show:
- ✅ All core files present
- ✅ API endpoints accessible
- ✅ Templates with Pro-Mep logo
- ✅ Vue components for Purchase Receipts
- ✅ Website settings configured
- ✅ Database setup complete

**Target Success Rate: >90%**

## 📞 Support

If validation fails or issues persist:
1. Check Frappe logs: `bench logs`
2. Run validation script: `bench execute material_requisition.validation.run_validation`
3. Check this checklist systematically
4. Ensure all Purchase Receipt files are present and pushed to git

---
**Last Updated**: After adding Purchase Receipt functionality and validation system
