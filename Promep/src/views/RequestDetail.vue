<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-gray-800 mb-2">📋 {{ requestId }}</h1>
          <p class="text-lg text-gray-600">Material Request Details</p>
        </div>
        <button
          @click="goBack"
          class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <ArrowLeft class="w-5 h-5" />
          <span>Back</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">Loading request details...</p>
      </div>

      <!-- Request Details -->
      <div v-else-if="request" class="space-y-6">
        <!-- Status and Basic Info -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-2xl font-bold text-gray-800">{{ request.name }}</h2>
              <p class="text-gray-600">Created on {{ formatDate(request.transaction_date) }}</p>
            </div>
            <span
              :class="getStatusBadgeClass(request.status)"
              class="px-6 py-3 rounded-xl text-lg font-bold"
            >
              {{ getStatusLabel(request.status) }}
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="font-semibold text-gray-700 mb-2">Project</h3>
              <p class="text-gray-800">{{ request.project || 'Not specified' }}</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-700 mb-2">Required By</h3>
              <p class="text-gray-800">{{ formatDate(request.schedule_date) }}</p>
            </div>
            <div v-if="request.remarks" class="md:col-span-2">
              <h3 class="font-semibold text-gray-700 mb-2">Notes</h3>
              <p class="text-gray-800">{{ request.remarks }}</p>
            </div>
          </div>
        </div>

        <!-- Items -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-6">Items ({{ request.items?.length || 0 }})</h3>
          <div class="space-y-4">
            <div
              v-for="item in request.items || []"
              :key="item.item_code"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Package class="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p class="font-medium text-gray-800">{{ item.item_name }}</p>
                  <p class="text-sm text-gray-600">{{ item.item_code }}</p>
                  <p class="text-sm text-gray-500">{{ item.description || 'No description' }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="font-semibold text-gray-800">{{ item.qty }} {{ item.uom }}</p>
                <div class="text-sm text-gray-600">
                  <p>Ordered: {{ item.ordered_qty || 0 }}</p>
                  <p>Received: {{ item.received_qty || 0 }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Purchase Orders -->
        <div v-if="request.purchase_orders?.length > 0" class="bg-white rounded-xl shadow-lg p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-6">Purchase Orders</h3>
          <div class="space-y-4">
            <div
              v-for="po in request.purchase_orders"
              :key="po.name"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div>
                <p class="font-medium text-gray-800">{{ po.name }}</p>
                <p class="text-sm text-gray-600">{{ po.supplier }}</p>
                <p class="text-sm text-gray-500">{{ formatDate(po.transaction_date) }}</p>
              </div>
              <div class="text-right">
                <span
                  :class="getPOStatusBadgeClass(po.status)"
                  class="px-3 py-1 rounded-full text-sm font-bold"
                >
                  {{ po.status }}
                </span>
                <p class="text-sm text-gray-600 mt-1">{{ formatCurrency(po.grand_total) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div v-if="request.status === 'pending'" class="bg-white rounded-xl shadow-lg p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-4">Actions</h3>
          <div class="flex space-x-4">
            <button
              @click="createPO"
              class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <ShoppingCart class="w-5 h-5" />
              <span>Create Purchase Order</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">❌</div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">Request not found</h3>
        <p class="text-gray-600 mb-6">The requested material request could not be found.</p>
        <button
          @click="goBack"
          class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Go Back
        </button>
      </div>
    </div>

    <!-- PO Creation Modal -->
    <POCreationModal
      v-if="showPOModal"
      :request="request"
      @close="closePOModal"
      @created="onPOCreated"
    />
  </div>
</template>

<script>
import { ArrowLeft, Package, ShoppingCart } from 'lucide-vue-next'
import POCreationModal from '../components/POCreationModal.vue'

export default {
  name: 'RequestDetail',
  components: {
    ArrowLeft,
    Package,
    ShoppingCart,
    POCreationModal
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
      request: null,
      showPOModal: false
    }
  },
  computed: {
    requestId() {
      return this.id || this.$route.params.id
    }
  },
  async mounted() {
    await this.loadRequest()
  },
  methods: {
    async loadRequest() {
      this.isLoading = true
      try {
        const response = await fetch('/api/method/material_requisition.api.material_request.get_request_detail', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
          },
          body: JSON.stringify({
            request_name: this.requestId
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        if (data.exc) {
          throw new Error(data.exc)
        }

        this.request = data.message
        if (this.request) {
          this.request.status = this.getRequestStatus(this.request)
        }

      } catch (error) {
        console.error('Failed to load request:', error)
        this.request = null
      } finally {
        this.isLoading = false
      }
    },

    goBack() {
      this.$router.go(-1)
    },

    createPO() {
      this.showPOModal = true
    },

    closePOModal() {
      this.showPOModal = false
    },

    onPOCreated() {
      this.closePOModal()
      this.loadRequest() // Refresh the request data
    },

    formatDate(dateString) {
      if (!dateString) return 'Not specified'
      return new Date(dateString).toLocaleDateString()
    },

    formatCurrency(amount) {
      if (!amount) return '₹0.00'
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
      }).format(amount)
    },

    getRequestStatus(request) {
      if (request.per_received === 100) {
        return 'received'
      } else if (request.per_ordered === 100) {
        return 'ordered'
      } else if (request.per_ordered > 0) {
        return 'partial'
      } else {
        return 'pending'
      }
    },

    getStatusLabel(status) {
      const statusMap = {
        'pending': 'Pending',
        'ordered': 'Ordered',
        'partial': 'Partially Received',
        'received': 'Received'
      }
      return statusMap[status] || status
    },

    getStatusBadgeClass(status) {
      const classMap = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'ordered': 'bg-blue-100 text-blue-800',
        'partial': 'bg-purple-100 text-purple-800',
        'received': 'bg-green-100 text-green-800'
      }
      return classMap[status] || 'bg-gray-100 text-gray-800'
    },

    getPOStatusBadgeClass(status) {
      const classMap = {
        'Draft': 'bg-gray-100 text-gray-800',
        'To Receive and Bill': 'bg-blue-100 text-blue-800',
        'To Bill': 'bg-yellow-100 text-yellow-800',
        'Completed': 'bg-green-100 text-green-800',
        'Cancelled': 'bg-red-100 text-red-800'
      }
      return classMap[status] || 'bg-gray-100 text-gray-800'
    }
  }
}
</script>
