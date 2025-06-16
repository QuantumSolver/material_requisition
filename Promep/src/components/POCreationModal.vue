<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b">
        <div>
          <h2 class="text-2xl font-bold text-gray-800">Create Purchase Order</h2>
          <p class="text-gray-600">{{ request?.name }}</p>
        </div>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Supplier Selection -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Supplier <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <select
              v-model="formData.supplier"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white"
              required
            >
              <option value="">Select a supplier...</option>
              <option
                v-for="supplier in suppliers"
                :key="supplier.name"
                :value="supplier.name"
              >
                {{ supplier.supplier_name }}
              </option>
            </select>
            <ChevronDown class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
          </div>
          <p v-if="!formData.supplier && showValidation" class="text-red-500 text-sm mt-1">
            Please select a supplier
          </p>
        </div>

        <!-- Required Date -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Required By <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.required_date"
            type="date"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :min="today"
            required
          />
          <p v-if="!formData.required_date && showValidation" class="text-red-500 text-sm mt-1">
            Please select a required date
          </p>
        </div>

        <!-- Items Preview -->
        <div class="mb-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-3">Items to Order</h3>
          <div class="bg-gray-50 rounded-lg p-4 max-h-48 overflow-y-auto">
            <div
              v-for="item in request?.items || []"
              :key="item.item_code"
              class="flex items-center justify-between py-2 border-b border-gray-200 last:border-b-0"
            >
              <div>
                <p class="font-medium text-gray-800">{{ item.item_name }}</p>
                <p class="text-sm text-gray-600">{{ item.item_code }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold text-gray-800">{{ item.qty }} {{ item.uom }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Notes -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            v-model="formData.notes"
            rows="3"
            placeholder="Add any special instructions for the supplier..."
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-4">
          <button
            @click="$emit('close')"
            class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="createPO"
            :disabled="isSubmitting || !isFormValid"
            :class="[
              'px-8 py-3 rounded-lg font-semibold flex items-center space-x-2 transition-all',
              isSubmitting || !isFormValid
                ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                : 'bg-green-500 hover:bg-green-600 text-white transform hover:scale-105 shadow-lg'
            ]"
          >
            <span v-if="isSubmitting">Creating PO...</span>
            <span v-else>Create Purchase Order</span>
            <ShoppingCart v-if="!isSubmitting" class="w-5 h-5" />
            <div v-else class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { X, ChevronDown, ShoppingCart } from 'lucide-vue-next'

export default {
  name: 'POCreationModal',
  components: {
    X,
    ChevronDown,
    ShoppingCart
  },
  props: {
    request: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'created'],
  data() {
    return {
      isSubmitting: false,
      showValidation: false,
      suppliers: [],
      formData: {
        supplier: '',
        required_date: this.getDefaultRequiredDate(),
        notes: ''
      }
    }
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    },
    isFormValid() {
      return this.formData.supplier && this.formData.required_date
    }
  },
  async mounted() {
    await this.loadSuppliers()
  },
  methods: {
    getDefaultRequiredDate() {
      const date = new Date()
      date.setDate(date.getDate() + 14) // Default to 2 weeks from now
      return date.toISOString().split('T')[0]
    },

    async loadSuppliers() {
      try {
        const response = await fetch('/api/method/material_requisition.api.purchase_order.get_suppliers', {
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

        this.suppliers = data.message || []
      } catch (error) {
        console.error('Failed to load suppliers:', error)
        this.suppliers = []
      }
    },

    async createPO() {
      if (!this.isFormValid) {
        this.showValidation = true
        return
      }

      this.isSubmitting = true

      try {
        const response = await fetch('/api/method/material_requisition.api.purchase_order.create_from_material_request', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || ''
          },
          body: JSON.stringify({
            material_request: this.request.name,
            supplier: this.formData.supplier,
            required_date: this.formData.required_date,
            notes: this.formData.notes
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        if (data.exc) {
          throw new Error(data.exc)
        }

        // Success
        this.showSuccessMessage(data.message?.name)
        this.$emit('created', data.message)

      } catch (error) {
        console.error('Failed to create PO:', error)
        this.showErrorMessage(error.message)
      } finally {
        this.isSubmitting = false
      }
    },

    showSuccessMessage(poName) {
      const notification = document.createElement('div')
      notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50'
      notification.textContent = `✅ Purchase Order ${poName} created successfully!`
      document.body.appendChild(notification)

      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification)
        }
      }, 3000)
    },

    showErrorMessage(message) {
      const notification = document.createElement('div')
      notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50'
      notification.textContent = `❌ Error: ${message}`
      document.body.appendChild(notification)

      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification)
        }
      }, 5000)
    }
  }
}
</script>
