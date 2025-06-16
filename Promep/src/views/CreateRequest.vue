<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
    <!-- Fixed Header -->
    <div class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button
            @click="goBack"
            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <span>←</span>
            <span>Back</span>
          </button>
          <div>
            <h1 class="text-2xl font-bold text-gray-800">📋 Create Material Request</h1>
            <p class="text-sm text-gray-600">Select items and quantities for your project</p>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="flex items-center space-x-4 text-sm">
          <div class="text-center">
            <div class="font-bold text-blue-600">{{ filteredItems.length }}</div>
            <div class="text-gray-500">Available</div>
          </div>
          <div class="text-center">
            <div class="font-bold text-green-600">{{ selectedItems.length }}</div>
            <div class="text-gray-500">Selected</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sticky Summary Section -->
    <div v-if="selectedItems.length > 0" class="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div class="max-w-7xl mx-auto px-6 py-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <h2 class="text-lg font-bold text-gray-800">Selected Items ({{ selectedItems.length }})</h2>
            <div class="text-sm text-gray-600">
              Total: {{ selectedItems.reduce((sum, item) => sum + item.qty, 0) }} items
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <button
              @click="clearAllSelections"
              class="text-red-600 hover:text-red-700 text-sm font-medium transition-colors"
            >
              Clear All
            </button>
            <button
              @click="submitRequest"
              :disabled="isSubmitting || selectedItems.length === 0"
              :class="[
                'px-6 py-2 rounded-lg font-medium text-sm transition-all',
                isSubmitting || selectedItems.length === 0
                  ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600 text-white shadow-md hover:shadow-lg'
              ]"
            >
              <span v-if="isSubmitting">Creating...</span>
              <span v-else>Create Request</span>
            </button>
          </div>
        </div>

        <!-- Date Fields Row -->
        <div class="mt-3 flex flex-col md:flex-row gap-3">
          <div class="flex-1">
            <label class="block text-xs font-medium text-gray-700 mb-1">Required By Date</label>
            <input
              v-model="requiredByDate"
              type="date"
              class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              :min="today"
            />
          </div>
          <div class="flex-1">
            <label class="block text-xs font-medium text-gray-700 mb-1">Expected Delivery Date</label>
            <input
              v-model="deliveryDate"
              type="date"
              class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              :min="requiredByDate || today"
            />
          </div>
          <div class="flex-1">
            <label class="block text-xs font-medium text-gray-700 mb-1">Notes (Optional)</label>
            <input
              v-model="notes"
              type="text"
              placeholder="Special instructions..."
              class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
          </div>
        </div>

        <!-- Compact Selected Items List -->
        <div class="mt-3 flex flex-wrap gap-2 max-h-24 overflow-y-auto">
          <div
            v-for="item in selectedItems"
            :key="item.item_code"
            class="flex items-center bg-green-50 border border-green-200 rounded-lg px-3 py-1 text-sm"
          >
            <span class="font-medium text-green-800">{{ item.item_name }}</span>
            <span class="mx-2 text-green-600">×{{ item.qty }}</span>
            <button
              @click="removeItem(item.item_code)"
              class="text-green-600 hover:text-red-600 ml-1 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-hidden">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center h-96">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p class="mt-4 text-gray-600">Loading items...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="max-w-7xl mx-auto px-6 py-6">
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong>Error:</strong> {{ error }}
          <button @click="loadItems" class="ml-4 underline">Try Again</button>
        </div>
      </div>

      <!-- Search and Filter Bar - Fixed Position -->
      <div v-else class="bg-white border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-6 py-3">
          <div class="flex flex-col md:flex-row gap-3">
            <div class="flex-1">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="🔍 Search for items by name or code..."
                class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
            <div class="md:w-48">
              <select
                v-model="selectedCategory"
                class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="">📦 All Categories</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ getCategoryIcon(category) }} {{ category }}
                </option>
              </select>
            </div>
            <button
              v-if="searchQuery || selectedCategory"
              @click="clearFilters"
              class="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors whitespace-nowrap"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Scrollable Items Grid -->
      <div class="flex-1 overflow-y-auto" :style="{ height: 'calc(100vh - ' + (selectedItems.length > 0 ? '220px' : '140px') + ')' }">
        <div class="max-w-7xl mx-auto px-6 py-6">

          <!-- Empty State -->
          <div v-if="filteredItems.length === 0" class="text-center py-16">
            <div class="text-6xl mb-4">
              {{ searchQuery || selectedCategory ? '🔍' : '📦' }}
            </div>
            <h3 class="text-xl font-bold text-gray-800 mb-2">
              {{ searchQuery || selectedCategory ? 'No items match your search' : 'No items found' }}
            </h3>
            <p class="text-gray-600 mb-6">
              {{ searchQuery || selectedCategory ? 'Try adjusting your search or filter criteria' : 'No items available' }}
            </p>
          </div>

          <!-- Items Grid -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div
              v-for="item in filteredItems"
              :key="item.item_code"
              :class="[
                'border border-gray-200 rounded-lg p-3 transition-all duration-200 cursor-pointer bg-white',
                'hover:shadow-md hover:border-blue-300 hover:scale-102',
                getItemQuantity(item.item_code) > 0 ? 'ring-2 ring-green-200 border-green-300 bg-green-50' : 'hover:bg-gray-50'
              ]"
              @click="quickAdd(item.item_code)"
            >
              <!-- Item Image -->
              <div class="w-full h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg mb-3 flex items-center justify-center relative overflow-hidden">
                <div class="text-3xl">{{ getItemIcon(item.item_group) }}</div>
                <div v-if="getItemQuantity(item.item_code) > 0" class="absolute top-1 right-1 bg-green-500 text-white text-xs px-1.5 py-0.5 rounded-full font-bold min-w-[20px] text-center">
                  {{ getItemQuantity(item.item_code) }}
                </div>
              </div>

              <!-- Item Info -->
              <div class="mb-3">
                <h3 class="font-semibold text-gray-800 mb-1 line-clamp-2 leading-tight text-sm">{{ item.item_name }}</h3>
                <p class="text-xs text-gray-600 mb-1">{{ item.item_code }}</p>
                <div class="flex items-center justify-between">
                  <p class="text-xs text-gray-500">{{ item.stock_uom }}</p>
                  <span class="text-xs bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full">
                    {{ item.item_group }}
                  </span>
                </div>
              </div>

              <!-- Quantity Selector -->
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-1.5">
                  <button
                    @click.stop="decreaseQuantity(item.item_code)"
                    :disabled="getItemQuantity(item.item_code) <= 0"
                    class="w-7 h-7 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-110 active:scale-95 text-sm"
                  >
                    -
                  </button>
                  <span class="w-8 text-center font-bold text-sm">{{ getItemQuantity(item.item_code) }}</span>
                  <button
                    @click.stop="increaseQuantity(item.item_code)"
                    class="w-7 h-7 bg-green-500 text-white rounded-full flex items-center justify-center hover:bg-green-600 transition-all duration-200 transform hover:scale-110 active:scale-95 text-sm"
                  >
                    +
                  </button>
                </div>
                <div v-if="getItemQuantity(item.item_code) > 0" class="text-green-600 font-medium flex items-center space-x-1">
                  <span class="text-xs">✓</span>
                </div>
                <div v-else class="text-gray-400 text-xs">
                  Click to add
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreateRequest',
  data() {
    return {
      isLoading: false,
      isSubmitting: false,
      error: null,
      items: [],
      selectedQuantities: {},
      searchQuery: '',
      selectedCategory: '',
      showSuccessMessage: false,
      lastCreatedRequest: null,
      requiredByDate: '',
      deliveryDate: '',
      notes: ''
    }
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    },
    categories() {
      const cats = [...new Set(this.items.map(item => item.item_group))].filter(Boolean)
      return cats.sort()
    },
    filteredItems() {
      let filtered = this.items

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(item =>
          item.item_name.toLowerCase().includes(query) ||
          item.item_code.toLowerCase().includes(query) ||
          (item.description && item.description.toLowerCase().includes(query))
        )
      }

      if (this.selectedCategory) {
        filtered = filtered.filter(item => item.item_group === this.selectedCategory)
      }

      return filtered
    },
    selectedItems() {
      return this.items
        .filter(item => this.selectedQuantities[item.item_code] > 0)
        .map(item => ({
          item_code: item.item_code,
          item_name: item.item_name,
          qty: this.selectedQuantities[item.item_code],
          uom: item.stock_uom
        }))
    }
  },
  async mounted() {
    console.log('CreateRequest component mounted')
    await this.loadItems()
  },
  methods: {
    async loadItems() {
      console.log('Loading items...')
      this.isLoading = true
      this.error = null

      try {
        const response = await fetch('/api/method/material_requisition.api.material_request.get_visual_items', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
          },
          body: JSON.stringify({})
        })

        console.log('Response status:', response.status)

        if (!response.ok) {
          if (response.status === 403) {
            throw new Error('Authentication required. Please refresh the page.')
          } else if (response.status === 500) {
            throw new Error('Server error. Please try again later.')
          } else {
            throw new Error(`Failed to load items (Status: ${response.status})`)
          }
        }

        const data = await response.json()
        console.log('Response data:', data)

        if (data.exc) {
          throw new Error(data.exc)
        }

        this.items = data.message || []
        console.log('Loaded items:', this.items.length)

        if (this.items.length === 0) {
          this.error = 'No items found in the system. Please contact your administrator.'
        }

      } catch (error) {
        console.error('Failed to load items:', error)
        this.error = error.message
        this.showNotification(`Failed to load items: ${error.message}`, 'error')
      } finally {
        this.isLoading = false
      }
    },

    getItemQuantity(itemCode) {
      return this.selectedQuantities[itemCode] || 0
    },

    increaseQuantity(itemCode) {
      console.log('Increasing quantity for:', itemCode)
      const currentQty = this.getItemQuantity(itemCode)
      // Create a new object to trigger reactivity
      this.selectedQuantities = {
        ...this.selectedQuantities,
        [itemCode]: currentQty + 1
      }
      console.log('New quantity:', this.selectedQuantities[itemCode])
    },

    decreaseQuantity(itemCode) {
      console.log('Decreasing quantity for:', itemCode)
      const current = this.getItemQuantity(itemCode)
      if (current > 0) {
        // Create a new object to trigger reactivity
        this.selectedQuantities = {
          ...this.selectedQuantities,
          [itemCode]: current - 1
        }
        console.log('New quantity:', this.selectedQuantities[itemCode])
      }
    },

    removeItem(itemCode) {
      console.log('Removing item:', itemCode)
      // Create a new object to trigger reactivity
      this.selectedQuantities = {
        ...this.selectedQuantities,
        [itemCode]: 0
      }
    },

    async submitRequest() {
      if (this.selectedItems.length === 0) {
        this.showNotification('Please select at least one item', 'error')
        return
      }

      console.log('Submitting request with items:', this.selectedItems)
      this.isSubmitting = true

      try {
        const response = await fetch('/api/method/material_requisition.api.material_request.create_simplified_material_request', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
          },
          body: JSON.stringify({
            items: this.selectedItems,
            notes: this.notes || 'Created from Promep interface',
            required_by_date: this.requiredByDate,
            delivery_date: this.deliveryDate
          })
        })

        if (!response.ok) {
          if (response.status === 403) {
            throw new Error('Authentication required. Please refresh the page and try again.')
          } else if (response.status === 500) {
            throw new Error('Server error. Please try again later.')
          } else {
            throw new Error(`Request failed with status: ${response.status}`)
          }
        }

        const data = await response.json()
        if (data.exc) {
          throw new Error(data.exc)
        }

        // Success
        this.lastCreatedRequest = data.message.name
        this.showNotification(`✅ Material Request ${data.message.name} created successfully!`, 'success')

        // Reset form
        this.selectedQuantities = {}
        this.searchQuery = ''
        this.selectedCategory = ''

        // Navigate after a short delay to show the success message
        setTimeout(() => {
          this.$router.push('/')
        }, 2000)

      } catch (error) {
        console.error('Failed to create request:', error)
        this.showNotification(`❌ Error: ${error.message}`, 'error')
      } finally {
        this.isSubmitting = false
      }
    },

    goBack() {
      this.$router.go(-1)
    },

    quickAdd(itemCode) {
      console.log('Quick add clicked for:', itemCode)
      this.increaseQuantity(itemCode)
    },

    clearFilters() {
      this.searchQuery = ''
      this.selectedCategory = ''
    },

    clearAllSelections() {
      console.log('Clearing all selections')
      this.selectedQuantities = {}
      this.requiredByDate = ''
      this.deliveryDate = ''
      this.notes = ''
    },

    getItemIcon(itemGroup) {
      const iconMap = {
        'Raw Material': '🔧',
        'Products': '📦',
        'Services': '⚙️',
        'Pipes': '🚰',
        'Fittings': '🔩',
        'Electrical': '⚡',
        'Hardware': '🔨',
        'Tools': '🛠️',
        'Safety': '🦺'
      }
      return iconMap[itemGroup] || '📦'
    },

    getCategoryIcon(category) {
      const iconMap = {
        'Raw Material': '🔧',
        'Products': '📦',
        'Services': '⚙️'
      }
      return iconMap[category] || '📦'
    },

    showNotification(message, type = 'success') {
      const notification = document.createElement('div')
      notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      }`
      notification.textContent = message
      document.body.appendChild(notification)

      setTimeout(() => {
        notification.style.transform = 'translateX(100%)'
        setTimeout(() => {
          if (document.body.contains(notification)) {
            document.body.removeChild(notification)
          }
        }, 300)
      }, 3000)
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Custom animations */
@keyframes pulse-green {
  0%, 100% {
    background-color: rgb(34, 197, 94);
  }
  50% {
    background-color: rgb(22, 163, 74);
  }
}

@keyframes pulse-red {
  0%, 100% {
    background-color: rgb(239, 68, 68);
  }
  50% {
    background-color: rgb(220, 38, 38);
  }
}

.animate-pulse-green {
  animation: pulse-green 2s infinite;
}

.animate-pulse-red {
  animation: pulse-red 2s infinite;
}

/* Smooth transitions for all interactive elements */
* {
  transition: all 0.2s ease-in-out;
}

/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Focus styles for accessibility */
input:focus,
select:focus,
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Loading animation enhancement */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Hover effects for cards */
.hover\:scale-105:hover {
  transform: scale(1.05);
}

.hover\:scale-102:hover {
  transform: scale(1.02);
}

/* Button press effect */
.active\:scale-95:active {
  transform: scale(0.95);
}

/* Smooth scrolling */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

/* Sticky positioning adjustments */
.sticky {
  position: -webkit-sticky;
  position: sticky;
}

/* Compact layout utilities */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
}

/* Enhanced grid responsiveness */
@media (min-width: 1536px) {
  .xl\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (min-width: 1792px) {
  .grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
</style>
