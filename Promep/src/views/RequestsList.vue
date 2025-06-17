<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-gray-800 mb-2">📋 Material Requests</h1>
          <p class="text-lg text-gray-600">Manage and track your material requisitions</p>
        </div>
        <div class="flex space-x-4">
          <button
            @click="goBack"
            class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <ArrowLeft class="w-5 h-5" />
            <span>Back</span>
          </button>
          <button
            @click="viewLineItems"
            class="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <Package class="w-5 h-5" />
            <span>Create PO</span>
          </button>
          <button
            @click="createNewRequest"
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <Plus class="w-5 h-5" />
            <span>New Request</span>
          </button>
        </div>
      </div>

      <!-- Status Filter Tabs -->
      <div class="flex space-x-2 mb-6 overflow-x-auto">
        <button
          v-for="status in statusFilters"
          :key="status.value"
          :class="[
            'px-6 py-3 rounded-lg font-medium transition-colors whitespace-nowrap flex items-center space-x-2',
            selectedStatus === status.value
              ? 'bg-blue-500 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
          ]"
          @click="selectStatus(status.value)"
        >
          <component :is="status.icon" class="w-5 h-5" />
          <span>{{ status.label }}</span>
          <span v-if="status.count > 0" class="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
            {{ status.count }}
          </span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">Loading requests...</p>
      </div>

      <!-- Requests Grid -->
      <div v-else-if="filteredRequests.length > 0" class="grid gap-6">
        <div
          v-for="request in filteredRequests"
          :key="request.name"
          class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
        >
          <div class="flex items-center justify-between mb-4">
            <div>
              <h3 class="text-xl font-bold text-gray-800">{{ request.name }}</h3>
              <p class="text-gray-600">{{ formatDate(request.transaction_date) }}</p>
            </div>
            <div class="flex items-center space-x-3">
              <span
                :class="getStatusBadgeClass(request.status)"
                class="px-4 py-2 rounded-lg text-sm font-bold"
              >
                {{ getStatusLabel(request.status) }}
              </span>
              <button
                @click="viewRequest(request.name)"
                class="text-blue-500 hover:text-blue-600"
              >
                <ChevronRight class="w-6 h-6" />
              </button>
            </div>
          </div>

          <!-- Items Summary -->
          <div class="mb-4">
            <p class="text-sm text-gray-600 mb-2">Items ({{ request.items?.length || 0 }})</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="item in (request.items || []).slice(0, 3)"
                :key="item.item_code"
                class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
              >
                {{ item.item_name }}
              </span>
              <span
                v-if="(request.items || []).length > 3"
                class="bg-gray-200 text-gray-600 px-3 py-1 rounded-full text-sm"
              >
                +{{ (request.items || []).length - 3 }} more
              </span>
            </div>
          </div>

          <!-- Purchase Order Actions -->
          <div v-if="request.status === 'pending'" class="border-t pt-4">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-gray-700">Create Purchase Order</p>
              <button
                @click="createPO(request)"
                class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Create PO
              </button>
            </div>
          </div>

          <!-- PO Information -->
          <div v-else-if="request.purchase_orders?.length > 0" class="border-t pt-4">
            <p class="text-sm font-medium text-gray-700 mb-2">Purchase Orders</p>
            <div class="space-y-2">
              <div
                v-for="po in request.purchase_orders"
                :key="po.name"
                class="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
              >
                <div>
                  <p class="font-medium text-gray-800">{{ po.name }}</p>
                  <p class="text-sm text-gray-600">{{ po.supplier }}</p>
                </div>
                <span
                  :class="getPOStatusBadgeClass(po.status)"
                  class="px-3 py-1 rounded-full text-xs font-bold"
                >
                  {{ po.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">📋</div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">No requests found</h3>
        <p class="text-gray-600 mb-6">
          {{ selectedStatus === 'all' ? 'No material requests yet' : `No ${selectedStatus} requests` }}
        </p>
        <button
          @click="createNewRequest"
          class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Create First Request
        </button>
      </div>
    </div>

    <!-- PO Creation Modal -->
    <POCreationModal
      v-if="showPOModal"
      :request="selectedRequest"
      @close="closePOModal"
      @created="onPOCreated"
    />
  </div>
</template>

<script>
import { ArrowLeft, Plus, ChevronRight, Clock, Package, Truck, CheckCircle, AlertCircle } from 'lucide-vue-next'
import POCreationModal from '../components/POCreationModal.vue'

export default {
  name: 'RequestsList',
  components: {
    ArrowLeft,
    Plus,
    ChevronRight,
    Package,
    Clock,
    Truck,
    CheckCircle,
    AlertCircle,
    POCreationModal
  },
  data() {
    return {
      isLoading: false,
      selectedStatus: 'all',
      requests: [],
      showPOModal: false,
      selectedRequest: null,
      statusFilters: [
        { value: 'all', label: 'All', icon: Package, count: 0 },
        { value: 'pending', label: 'Pending', icon: Clock, count: 0 },
        { value: 'ordered', label: 'Ordered', icon: Package, count: 0 },
        { value: 'partial', label: 'Partial', icon: Truck, count: 0 },
        { value: 'received', label: 'Received', icon: CheckCircle, count: 0 }
      ]
    }
  },
  computed: {
    filteredRequests() {
      if (this.selectedStatus === 'all') {
        return this.requests
      }
      return this.requests.filter(request => request.status === this.selectedStatus)
    }
  },
  mounted() {
    this.loadRequests()
    // Check for status filter from query params
    if (this.$route.query.status) {
      this.selectedStatus = this.$route.query.status
    }
  },
  methods: {
    async loadRequests() {
      this.isLoading = true
      try {
        const response = await fetch('/api/method/material_requisition.api.material_request.get_requests_with_po_status', {
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

        this.requests = (data.message || []).map(req => ({
          ...req,
          status: this.getRequestStatus(req)
        }))

        this.updateStatusCounts()

      } catch (error) {
        console.error('Failed to load requests:', error)
        this.requests = []
      } finally {
        this.isLoading = false
      }
    },

    updateStatusCounts() {
      const counts = { all: this.requests.length, pending: 0, ordered: 0, partial: 0, received: 0 }
      
      this.requests.forEach(request => {
        if (counts[request.status] !== undefined) {
          counts[request.status]++
        }
      })

      this.statusFilters.forEach(filter => {
        filter.count = counts[filter.value] || 0
      })
    },

    selectStatus(status) {
      this.selectedStatus = status
      // Update URL without navigation
      this.$router.replace({ query: { ...this.$route.query, status: status === 'all' ? undefined : status } })
    },

    goBack() {
      this.$router.go(-1)
    },

    createNewRequest() {
      this.$router.push('/create-request')
    },

    viewLineItems() {
      this.$router.push('/line-items')
    },

    viewRequest(requestName) {
      this.$router.push(`/request/${requestName}`)
    },

    createPO(request) {
      this.selectedRequest = request
      this.showPOModal = true
    },

    closePOModal() {
      this.showPOModal = false
      this.selectedRequest = null
    },

    onPOCreated() {
      this.closePOModal()
      this.loadRequests() // Refresh the list
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
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
