<template>
  <div
    :class="[
      'rounded-3xl p-8 cursor-pointer transform hover:scale-110 transition-all duration-300 shadow-2xl text-white touch-target',
      status.color
    ]"
    @click="$emit('click')"
  >
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-2xl font-bold mb-4">{{ status.label }}</h3>
        <p class="text-6xl font-black">{{ status.count }}</p>
      </div>
      <div class="opacity-90">
        <component :is="status.icon" class="w-20 h-20" />
      </div>
    </div>

    <!-- Progress indicator -->
    <div class="mt-6">
      <div class="bg-white bg-opacity-30 rounded-full h-2">
        <div
          class="bg-white rounded-full h-2 transition-all duration-500"
          :style="{ width: getProgressWidth() }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatusCard',
  props: {
    status: {
      type: Object,
      required: true
    }
  },
  emits: ['click'],
  methods: {
    getProgressWidth() {
      // Simple progress calculation based on count
      const maxCount = 50; // Assume max of 50 for demo
      const percentage = Math.min((this.status.count / maxCount) * 100, 100);
      return `${percentage}%`;
    }
  }
}
</script>
