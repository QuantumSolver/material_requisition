<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Header with logout button -->
    <header v-if="$auth.isLoggedIn" class="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div class="flex justify-between items-center max-w-7xl mx-auto">
        <h1 class="text-xl font-semibold text-gray-800">Material Requisition System</h1>
        <button
          @click="$auth.logout()"
          class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors duration-200"
        >
          Logout
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
  inject: ['$auth']
};
</script>

<style>
#app {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
</style>
