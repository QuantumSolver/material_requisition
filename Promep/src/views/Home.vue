<template>
  <div class="min-h-screen bg-dashboard p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-16">
        <h1 class="text-construction-xl mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Pro-Mep
        </h1>
        <!-- <p class="text-construction text-gray-700">Quick and easy material requests for construction teams</p> -->
      </div>

      <!-- Primary Action Buttons -->
      <div class="flex flex-col md:flex-row justify-center items-center gap-6 mb-16">
        <button
          @click="createNewRequest"
          class="btn-primary-xl flex items-center space-x-6 shadow-2xl"
        >
          <Plus class="w-12 h-12" />
          <span>Create Material Requisition</span>
        </button>
        <button
          @click="viewLineItems"
          class="bg-purple-500 hover:bg-purple-600 text-white px-8 py-6 rounded-2xl text-2xl font-bold flex items-center space-x-6 shadow-2xl transition-all duration-300 transform hover:scale-105"
        >
          <Package class="w-12 h-12" />
          <span>Create Purchase Order</span>
        </button>

        <button
          @click="viewReceipts"
          class="bg-green-500 hover:bg-green-600 text-white px-8 py-6 rounded-2xl text-2xl font-bold flex items-center space-x-6 shadow-2xl transition-all duration-300 transform hover:scale-105"
        >
          <Truck class="w-12 h-12" />
          <span>Purchase Receipts</span>
        </button>
      </div>

      <!-- Status Overview Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
        <StatusCard
          v-for="status in statusCards"
          :key="status.type"
          :status="status"
          @click="viewRequests(status.type)"
        />
      </div>

      <!-- Recent Requests -->
      <div class="card">
        <h2 class="text-construction-lg mb-8 text-center">Recent Requests</h2>
        <div v-if="recentRequests.length === 0" class="text-center py-12">
          <div class="text-6xl mb-4">📋</div>
          <p class="text-construction text-gray-500">No recent requests</p>
          <p class="text-lg text-gray-400 mt-2">Create your first material request above!</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="request in recentRequests"
            :key="request.name"
            class="card-interactive"
            @click="viewRequest(request.name)"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-xl font-bold text-gray-800 mb-2">{{ request.name }}</h3>
                <p class="text-lg text-gray-600">{{ formatDate(request.transaction_date) }}</p>
              </div>
              <div class="flex items-center space-x-4">
                <span
                  :class="getStatusBadgeClass(request.status)"
                  class="px-6 py-3 rounded-2xl text-lg font-bold"
                >
                  {{ getStatusLabel(request.status) }}
                </span>
                <ChevronRight class="w-8 h-8 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Plus, ChevronRight, Clock, Package, Truck, CheckCircle } from 'lucide-vue-next'
import StatusCard from '../components/StatusCard.vue'

export default {
  name: 'Home',
  components: {
    Plus,
    ChevronRight,
    Package,
    Truck,
    StatusCard
  },
  data() {
    return {
      statusCards: [
        {
          type: 'pending',
          label: 'Pending',
          count: 0,
          icon: Clock,
          color: 'status-pending'
        },
        {
          type: 'ordered',
          label: 'Ordered',
          count: 0,
          icon: Package,
          color: 'status-ordered'
        },
        {
          type: 'partial',
          label: 'Partially Received',
          count: 0,
          icon: Truck,
          color: 'status-partial'
        },
        {
          type: 'received',
          label: 'Received',
          count: 0,
          icon: CheckCircle,
          color: 'status-received'
        }
      ],
      recentRequests: []
    }
  },
  mounted() {
    this.loadDashboardData()
  },
  beforeUnmount() {
    // Clean up resources to prevent memory leaks
    if (this.$resources && this.$resources.dashboardData) {
      this.$resources.dashboardData = null
    }
  },
  methods: {
    createNewRequest() {
      console.log('Navigating to create-request...');
      console.log('Current route:', this.$route.path);
      console.log('Router instance:', this.$router);

      this.$router.push('/create-request').then(() => {
        console.log('Navigation successful to:', this.$route.path);
      }).catch(error => {
        console.error('Navigation failed:', error);
      });
    },
    viewRequests(status) {
      this.$router.push(`/requests?status=${status}`)
    },
    viewRequest(requestName) {
      this.$router.push(`/request/${requestName}`)
    },
    viewLineItems() {
      this.$router.push('/line-items')
    },
    viewReceipts() {
      this.$router.push('/receipts')
    },
    async loadDashboardData() {
      try {
        const response = await fetch('/api/method/material_requisition.api.dashboard.get_dashboard_data', {
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

        const result = data.message || {}

        // Update status counts
        if (result.status_counts) {
          result.status_counts.forEach(item => {
            const card = this.statusCards.find(c => c.type === item.status)
            if (card) {
              card.count = item.count
            }
          })
        }

        // Update recent requests
        if (result.recent_requests) {
          this.recentRequests = result.recent_requests.map(req => ({
            ...req,
            status: this.getRequestStatus(req)
          }))
        }

      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    getStatusLabel(status) {
      const statusMap = {
        'pending': 'Pending',
        'ordered': 'Ordered',
        'partial': 'Partial',
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
    }
  }
}
</script>
