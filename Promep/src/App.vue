<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Header with navigation button -->
    <header v-if="$auth.isLoggedIn" class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <h1 class="text-xl font-semibold text-gray-800">Pro-mep</h1>
        <button
          @click="goToHome()"
          class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          <span>Back to Home</span>
        </button>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  inject: ['$auth'],
  methods: {
    goToHome() {
      // Navigate to main Frappe desk/app interface
      window.location.href = '/app';
    }
  }
};
</script>

<style>
#app {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
</style>
