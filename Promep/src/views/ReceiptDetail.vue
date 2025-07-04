<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-gray-800 mb-2">📦 {{ receiptId }}</h1>
          <p class="text-lg text-gray-600">Purchase Receipt Details</p>
        </div>
        <div class="flex space-x-3">
          <button
            @click="openInERPNext"
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <ExternalLink class="w-5 h-5" />
            <span>Open in ERPNext</span>
          </button>
          <button
            @click="goBack"
            class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <ArrowLeft class="w-5 h-5" />
            <span>Back</span>
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">Loading receipt details...</p>
      </div>

      <!-- Receipt Details -->
      <div v-else-if="receipt" class="space-y-6">
        <!-- Basic Information -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">Receipt Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <p class="text-sm text-gray-600">Supplier</p>
              <p class="text-lg font-medium text-gray-800">{{ receipt.supplier }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Posting Date</p>
              <p class="text-lg font-medium text-gray-800">{{ formatDate(receipt.posting_date) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Status</p>
              <span
                :class="[getStatusBadgeClass(receipt.docstatus), 'px-3 py-1 rounded-full text-sm font-bold']"
              >
                {{ getStatusLabel(receipt.docstatus) }}
              </span>
            </div>
            <div>
              <p class="text-sm text-gray-600">Grand Total</p>
              <p class="text-lg font-medium text-gray-800">{{ formatCurrency(receipt.grand_total) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Company</p>
              <p class="text-lg font-medium text-gray-800">{{ receipt.company }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Created By</p>
              <p class="text-lg font-medium text-gray-800">{{ receipt.owner }}</p>
            </div>
          </div>
          <div v-if="receipt.remarks" class="mt-4">
            <p class="text-sm text-gray-600">Remarks</p>
            <p class="text-gray-800">{{ receipt.remarks }}</p>
          </div>
        </div>

        <!-- Related Documents -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Material Requests -->
          <div v-if="receipt.material_requests && receipt.material_requests.length > 0" class="bg-white rounded-xl shadow-lg p-6">
            <h3 class="text-xl font-bold text-gray-800 mb-4">📋 Related Material Requests</h3>
            <div class="space-y-2">
              <div
                v-for="mr in receipt.material_requests"
                :key="mr"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <span class="font-medium text-gray-800">{{ mr }}</span>
                <div class="flex space-x-2">
                  <button
                    @click="viewMaterialRequest(mr)"
                    class="text-blue-500 hover:text-blue-600 text-sm"
                  >
                    View
                  </button>
                  <button
                    @click="openMRInERPNext(mr)"
                    class="text-blue-500 hover:text-blue-700 transition-colors"
                    title="Open in ERPNext"
                  >
                    <ExternalLink class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Purchase Orders -->
          <div v-if="receipt.purchase_orders && receipt.purchase_orders.length > 0" class="bg-white rounded-xl shadow-lg p-6">
            <h3 class="text-xl font-bold text-gray-800 mb-4">🛒 Related Purchase Orders</h3>
            <div class="space-y-2">
              <div
                v-for="po in receipt.purchase_orders"
                :key="po.purchase_order"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div>
                  <p class="font-medium text-gray-800">{{ po.purchase_order }}</p>
                  <p class="text-sm text-gray-600">{{ po.supplier }}</p>
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="openPOInERPNext(po.purchase_order)"
                    class="text-blue-500 hover:text-blue-700 transition-colors"
                    title="Open in ERPNext"
                  >
                    <ExternalLink class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Items Received -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">📦 Items Received</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-left py-3 px-4 font-medium text-gray-700">Item</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700">Description</th>
                  <th class="text-right py-3 px-4 font-medium text-gray-700">Qty</th>
                  <th class="text-right py-3 px-4 font-medium text-gray-700">Received</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700">UOM</th>
                  <th class="text-right py-3 px-4 font-medium text-gray-700">Rate</th>
                  <th class="text-right py-3 px-4 font-medium text-gray-700">Amount</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700">Warehouse</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in receipt.items"
                  :key="item.item_code"
                  class="border-b border-gray-100 hover:bg-gray-50"
                >
                  <td class="py-3 px-4">
                    <div>
                      <p class="font-medium text-gray-800">{{ item.item_code }}</p>
                      <p class="text-sm text-gray-600">{{ item.item_name }}</p>
                    </div>
                  </td>
                  <td class="py-3 px-4 text-gray-600">{{ item.description }}</td>
                  <td class="py-3 px-4 text-right text-gray-800">{{ item.qty }}</td>
                  <td class="py-3 px-4 text-right">
                    <span class="font-medium text-green-600">{{ item.received_qty }}</span>
                  </td>
                  <td class="py-3 px-4 text-gray-600">{{ item.uom }}</td>
                  <td class="py-3 px-4 text-right text-gray-800">{{ formatCurrency(item.rate) }}</td>
                  <td class="py-3 px-4 text-right text-gray-800">{{ formatCurrency(item.amount) }}</td>
                  <td class="py-3 px-4 text-gray-600">{{ item.warehouse }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">❌</div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">Receipt not found</h3>
        <p class="text-gray-600 mb-6">The requested purchase receipt could not be loaded.</p>
        <button
          @click="goBack"
          class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Go Back
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ArrowLeft, ExternalLink } from 'lucide-vue-next'

export default {
  name: 'ReceiptDetail',
  
  components: {
    ArrowLeft,
    ExternalLink
  },

  props: {
    id: {
      type: String,
      required: true
    }
  },

  data() {
    return {
      isLoading: false,
      receipt: null
    }
  },

  computed: {
    receiptId() {
      return this.id
    }
  },

  mounted() {
    this.loadReceipt()
  },

  methods: {
    async loadReceipt() {
      this.isLoading = true
      try {
        const response = await fetch('/api/method/material_requisition.api.purchase_receipt.get_receipt_detail', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
          },
          body: JSON.stringify({
            receipt_name: this.receiptId
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        if (data.exc) {
          throw new Error(data.exc)
        }

        this.receipt = data.message
      } catch (error) {
        console.error('Failed to load receipt:', error)
        this.receipt = null
      } finally {
        this.isLoading = false
      }
    },

    goBack() {
      this.$router.go(-1)
    },

    openInERPNext() {
      // Open Purchase Receipt in ERPNext in a new tab
      const erpnext_url = `/app/purchase-receipt/${this.receiptId}`
      window.open(erpnext_url, '_blank')
    },

    viewMaterialRequest(requestName) {
      this.$router.push(`/request/${requestName}`)
    },

    openMRInERPNext(requestName) {
      // Open Material Request in ERPNext in a new tab
      const erpnext_url = `/app/material-request/${requestName}`
      window.open(erpnext_url, '_blank')
    },

    openPOInERPNext(poName) {
      // Open Purchase Order in ERPNext in a new tab
      const erpnext_url = `/app/purchase-order/${poName}`
      window.open(erpnext_url, '_blank')
    },

    formatDate(date) {
      return new Date(date).toLocaleDateString()
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount || 0)
    },

    getStatusLabel(docstatus) {
      return {
        0: 'Draft',
        1: 'Submitted',
        2: 'Cancelled'
      }[docstatus] || 'Unknown'
    },

    getStatusBadgeClass(docstatus) {
      return {
        0: 'bg-gray-100 text-gray-800',
        1: 'bg-green-100 text-green-800',
        2: 'bg-red-100 text-red-800'
      }[docstatus] || 'bg-gray-100 text-gray-800'
    }
  }
}
</script>
