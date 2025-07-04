<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-gray-800 mb-2">📦 Purchase Receipts</h1>
          <p class="text-lg text-gray-600">Track received materials and goods</p>
        </div>
        <div class="flex space-x-4">
          <button
            @click="goBack"
            class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <ArrowLeft class="w-5 h-5" />
            <span>Back</span>
          </button>
        </div>
      </div>

      <!-- Status Filters -->
      <div class="flex space-x-2 mb-6 overflow-x-auto">
        <button
          v-for="filter in statusFilters"
          :key="filter.value"
          :class="[
            'px-6 py-3 rounded-lg font-medium transition-colors whitespace-nowrap flex items-center space-x-2',
            selectedStatus === filter.value
              ? 'bg-blue-500 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
          ]"
          @click="selectStatus(filter.value)"
        >
          <component :is="filter.icon" class="w-5 h-5" />
          <span>{{ filter.label }}</span>
          <span v-if="filter.count > 0" class="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
            {{ filter.count }}
          </span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">Loading receipts...</p>
      </div>

      <!-- Receipts List -->
      <div v-else-if="filteredReceipts.length > 0" class="grid gap-6">
        <div
          v-for="receipt in filteredReceipts"
          :key="receipt.name"
          class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-2">
              <div>
                <h3 class="text-xl font-bold text-gray-800">{{ receipt.name }}</h3>
                <p class="text-gray-600">{{ formatDate(receipt.posting_date) }}</p>
              </div>
              <button
                @click="openInERPNext(receipt.name)"
                class="text-blue-500 hover:text-blue-700 transition-colors"
                title="Open in ERPNext"
              >
                <ExternalLink class="w-4 h-4" />
              </button>
            </div>
            <div class="flex items-center space-x-3">
              <span
                :class="[getStatusBadgeClass(receipt.receipt_status), 'px-4 py-2 rounded-lg text-sm font-bold']"
              >
                {{ receipt.receipt_status }}
              </span>
              <button
                @click="viewReceipt(receipt.name)"
                class="text-blue-500 hover:text-blue-600"
              >
                <ChevronRight class="w-6 h-6" />
              </button>
            </div>
          </div>

          <!-- Receipt Details -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <p class="text-sm text-gray-600">Supplier</p>
              <p class="font-medium text-gray-800">{{ receipt.supplier }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Total Items</p>
              <p class="font-medium text-gray-800">{{ receipt.total_items || 0 }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-600">Grand Total</p>
              <p class="font-medium text-gray-800">{{ formatCurrency(receipt.grand_total) }}</p>
            </div>
          </div>

          <!-- Related Purchase Orders -->
          <div v-if="receipt.purchase_orders && receipt.purchase_orders.length > 0" class="border-t pt-4">
            <p class="text-sm font-medium text-gray-700 mb-2">Related Purchase Orders</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="po in receipt.purchase_orders"
                :key="po"
                class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center space-x-1"
              >
                <span>{{ po }}</span>
                <button
                  @click="openPOInERPNext(po)"
                  class="text-blue-600 hover:text-blue-800 transition-colors"
                  title="Open PO in ERPNext"
                >
                  <ExternalLink class="w-3 h-3" />
                </button>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">📦</div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">No receipts found</h3>
        <p class="text-gray-600 mb-6">
          {{ selectedStatus === 'all' ? 'No purchase receipts yet' : `No ${selectedStatus} receipts` }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ArrowLeft, ChevronRight, Package, FileText, CheckCircle, XCircle, ExternalLink } from 'lucide-vue-next'

export default {
  name: 'ReceiptsList',
  
  components: {
    ArrowLeft,
    ChevronRight,
    Package,
    FileText,
    CheckCircle,
    XCircle,
    ExternalLink
  },

  data() {
    return {
      isLoading: false,
      selectedStatus: 'all',
      receipts: [],
      statusFilters: [
        { value: 'all', label: 'All', icon: Package, count: 0 },
        { value: 'draft', label: 'Draft', icon: FileText, count: 0 },
        { value: 'submitted', label: 'Submitted', icon: CheckCircle, count: 0 },
        { value: 'cancelled', label: 'Cancelled', icon: XCircle, count: 0 }
      ]
    }
  },

  computed: {
    filteredReceipts() {
      if (this.selectedStatus === 'all') {
        return this.receipts
      }
      return this.receipts.filter(receipt => 
        receipt.receipt_status.toLowerCase() === this.selectedStatus
      )
    }
  },

  mounted() {
    this.loadReceipts()
    if (this.$route.query.status) {
      this.selectedStatus = this.$route.query.status
    }
  },

  methods: {
    async loadReceipts() {
      this.isLoading = true
      try {
        const response = await fetch('/api/method/material_requisition.api.purchase_receipt.get_purchase_receipts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        if (data.exc) {
          throw new Error(data.exc)
        }

        this.receipts = data.message?.receipts || []
        this.updateStatusCounts()
      } catch (error) {
        console.error('Failed to load receipts:', error)
        this.receipts = []
      } finally {
        this.isLoading = false
      }
    },

    updateStatusCounts() {
      const counts = {
        all: this.receipts.length,
        draft: 0,
        submitted: 0,
        cancelled: 0
      }

      this.receipts.forEach(receipt => {
        const status = receipt.receipt_status.toLowerCase()
        if (counts[status] !== undefined) {
          counts[status]++
        }
      })

      this.statusFilters.forEach(filter => {
        filter.count = counts[filter.value] || 0
      })
    },

    selectStatus(status) {
      this.selectedStatus = status
      this.$router.replace({
        query: {
          ...this.$route.query,
          status: status === 'all' ? undefined : status
        }
      })
    },

    goBack() {
      this.$router.go(-1)
    },

    viewReceipt(receiptName) {
      this.$router.push(`/receipt/${receiptName}`)
    },

    openInERPNext(receiptName) {
      // Open Purchase Receipt in ERPNext in a new tab
      const erpnext_url = `/app/purchase-receipt/${receiptName}`
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

    getStatusBadgeClass(status) {
      return {
        'Draft': 'bg-gray-100 text-gray-800',
        'Submitted': 'bg-green-100 text-green-800',
        'Cancelled': 'bg-red-100 text-red-800'
      }[status] || 'bg-gray-100 text-gray-800'
    }
  }
}
</script>
