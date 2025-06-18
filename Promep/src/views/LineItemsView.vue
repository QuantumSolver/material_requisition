<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-gray-800 mb-2">🛒 Create Purchase Order</h1>
          <p class="text-lg text-gray-600">Select individual items from material requests to create purchase orders</p>
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
            v-if="selectedItems.length > 0"
            @click="createPOFromSelected"
            class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <ShoppingCart class="w-5 h-5" />
            <span>Create PO ({{ selectedItems.length }})</span>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Status Filter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              v-model="filters.status"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="partial">Partially Ordered</option>
              <option value="ordered">Ordered</option>
              <option value="received">Received</option>
            </select>
          </div>

          <!-- Item Search -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Search Items</label>
            <input
              v-model="filters.item"
              @input="debounceSearch"
              type="text"
              placeholder="Item code or name..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Selection Actions -->
          <div class="flex items-end space-x-2">
            <button
              @click="selectAll"
              class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              Select All
            </button>
            <button
              @click="clearSelection"
              class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              Clear
            </button>
          </div>

          <!-- Selected Count -->
          <div class="flex items-end">
            <div class="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg text-sm font-medium">
              {{ selectedItems.length }} items selected
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">Loading line items...</p>
      </div>

      <!-- Line Items Table -->
      <div v-else-if="lineItems.length > 0" class="bg-white rounded-xl shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-4 text-left">
                  <input
                    type="checkbox"
                    :checked="isAllSelected"
                    @change="toggleSelectAll"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Item</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Quantity</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Status</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Material Request</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Suppliers</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr
                v-for="item in lineItems"
                :key="item.line_item_id"
                :class="[
                  'hover:bg-gray-50 transition-colors',
                  selectedItems.includes(item.line_item_id) ? 'bg-blue-50' : ''
                ]"
              >
                <td class="px-6 py-4">
                  <input
                    type="checkbox"
                    :value="item.line_item_id"
                    v-model="selectedItems"
                    :disabled="item.item_status === 'received' || item.pending_qty <= 0"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </td>
                <td class="px-6 py-4">
                  <div>
                    <p class="font-medium text-gray-800">{{ item.item_name }}</p>
                    <p class="text-sm text-gray-600">{{ item.item_code }}</p>
                    <p class="text-xs text-gray-500">{{ item.description || 'No description' }}</p>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm">
                    <p class="font-semibold text-gray-800">{{ item.qty }} {{ item.uom }}</p>
                    <p class="text-gray-600">Ordered: {{ item.ordered_qty || 0 }}</p>
                    <p class="text-gray-600">Received: {{ item.received_qty || 0 }}</p>
                    <p class="text-green-600 font-medium">Pending: {{ item.pending_qty || 0 }}</p>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="getStatusBadgeClass(item.item_status)"
                    class="px-3 py-1 rounded-full text-xs font-bold"
                  >
                    {{ getStatusLabel(item.item_status) }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm">
                    <p class="font-medium text-gray-800">{{ item.material_request }}</p>
                    <p class="text-gray-600">{{ formatDate(item.transaction_date) }}</p>
                    <p class="text-gray-500">{{ item.project || 'No project' }}</p>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-xs space-y-1">
                    <span
                      v-for="supplier in item.suppliers.slice(0, 2)"
                      :key="supplier.supplier"
                      class="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded mr-1"
                    >
                      {{ supplier.supplier_name }}
                    </span>
                    <span
                      v-if="item.suppliers.length > 2"
                      class="inline-block bg-gray-200 text-gray-600 px-2 py-1 rounded text-xs"
                    >
                      +{{ item.suppliers.length - 2 }} more
                    </span>
                    <span
                      v-if="item.suppliers.length === 0"
                      class="text-gray-500 text-xs"
                    >
                      No suppliers
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex space-x-2">
                    <button
                      @click="viewMaterialRequest(item.material_request)"
                      class="text-blue-500 hover:text-blue-600 text-sm"
                    >
                      View MR
                    </button>
                    <button
                      @click="openMRInERPNext(item.material_request)"
                      class="text-blue-500 hover:text-blue-700 transition-colors"
                      title="Open in ERPNext"
                    >
                      <ExternalLink class="w-3 h-3" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalCount > lineItems.length" class="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <p class="text-sm text-gray-600">
            Showing {{ lineItems.length }} of {{ totalCount }} items
          </p>
          <button
            v-if="hasMore"
            @click="loadMore"
            :disabled="isLoadingMore"
            class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {{ isLoadingMore ? 'Loading...' : 'Load More' }}
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="text-6xl mb-4">🛒</div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">No items available for purchase orders</h3>
        <p class="text-gray-600 mb-6">No items match your current filters or all items have been ordered</p>
        <button
          @click="clearFilters"
          class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Selective PO Creation Modal -->
    <SelectivePOCreationModal
      v-if="showPOModal"
      :selectedItems="selectedItemsData"
      @close="closePOModal"
      @created="onPOCreated"
    />
  </div>
</template>

<script>
import { ArrowLeft, ShoppingCart, ExternalLink } from 'lucide-vue-next'
import SelectivePOCreationModal from '../components/SelectivePOCreationModal.vue'

export default {
  name: 'LineItemsView',
  components: {
    ArrowLeft,
    ShoppingCart,
    ExternalLink,
    SelectivePOCreationModal
  },
  data() {
    return {
      isLoading: false,
      isLoadingMore: false,
      lineItems: [],
      selectedItems: [],
      totalCount: 0,
      hasMore: false,
      showPOModal: false,
      filters: {
        status: 'all',
        item: '',
        supplier: ''
      },
      searchTimeout: null
    }
  },
  computed: {
    isAllSelected() {
      const selectableItems = this.lineItems.filter(item => 
        item.item_status !== 'received' && item.pending_qty > 0
      )
      return selectableItems.length > 0 && selectableItems.every(item => 
        this.selectedItems.includes(item.line_item_id)
      )
    },
    selectedItemsData() {
      return this.lineItems.filter(item => 
        this.selectedItems.includes(item.line_item_id)
      )
    }
  },
  mounted() {
    this.loadLineItems()
  },
  methods: {
    async loadLineItems(append = false) {
      if (!append) {
        this.isLoading = true
        this.lineItems = []
      } else {
        this.isLoadingMore = true
      }

      try {
        const offset = append ? this.lineItems.length : 0
        const response = await fetch('/api/method/material_requisition.api.material_request.get_line_items', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
          },
          body: JSON.stringify({
            status_filter: this.filters.status,
            item_filter: this.filters.item,
            supplier_filter: this.filters.supplier,
            limit: 50,
            offset: offset
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        if (data.exc) {
          throw new Error(data.exc)
        }

        const result = data.message || { line_items: [], total_count: 0, has_more: false }
        
        if (append) {
          this.lineItems.push(...result.line_items)
        } else {
          this.lineItems = result.line_items
        }
        
        this.totalCount = result.total_count
        this.hasMore = result.has_more

      } catch (error) {
        console.error('Failed to load line items:', error)
        if (!append) {
          this.lineItems = []
        }
      } finally {
        this.isLoading = false
        this.isLoadingMore = false
      }
    },

    loadMore() {
      this.loadLineItems(true)
    },

    applyFilters() {
      this.selectedItems = []
      this.loadLineItems()
    },

    debounceSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.applyFilters()
      }, 500)
    },

    clearFilters() {
      this.filters = {
        status: 'all',
        item: '',
        supplier: ''
      }
      this.applyFilters()
    },

    selectAll() {
      const selectableItems = this.lineItems.filter(item => 
        item.item_status !== 'received' && item.pending_qty > 0
      )
      this.selectedItems = selectableItems.map(item => item.line_item_id)
    },

    clearSelection() {
      this.selectedItems = []
    },

    toggleSelectAll() {
      if (this.isAllSelected) {
        this.clearSelection()
      } else {
        this.selectAll()
      }
    },

    createPOFromSelected() {
      if (this.selectedItems.length === 0) return
      this.showPOModal = true
    },

    closePOModal() {
      this.showPOModal = false
    },

    onPOCreated() {
      this.closePOModal()
      this.selectedItems = []
      this.loadLineItems() // Refresh the list
    },

    goBack() {
      this.$router.go(-1)
    },

    viewMaterialRequest(requestName) {
      this.$router.push(`/request/${requestName}`)
    },

    openMRInERPNext(requestName) {
      // Open Material Request in ERPNext in a new tab
      const erpnext_url = `/app/material-request/${requestName}`
      window.open(erpnext_url, '_blank')
    },

    formatDate(dateString) {
      if (!dateString) return 'Not specified'
      return new Date(dateString).toLocaleDateString()
    },

    getStatusLabel(status) {
      const statusMap = {
        'pending': 'Pending',
        'ordered': 'Ordered',
        'partial': 'Partially Ordered',
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
    }
  }
}
</script>
