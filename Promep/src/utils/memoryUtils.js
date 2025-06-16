/**
 * Memory leak detection and prevention utilities
 */

class MemoryTracker {
  constructor() {
    this.componentInstances = new Map()
    this.fetchRequests = new Set()
    this.timers = new Set()
    this.eventListeners = new Map()
  }

  // Track component instances
  trackComponent(componentName, instance) {
    if (!this.componentInstances.has(componentName)) {
      this.componentInstances.set(componentName, new Set())
    }
    this.componentInstances.get(componentName).add(instance)
    console.log(`Tracking component: ${componentName}, total instances: ${this.componentInstances.get(componentName).size}`)
  }

  // Untrack component instances
  untrackComponent(componentName, instance) {
    if (this.componentInstances.has(componentName)) {
      this.componentInstances.get(componentName).delete(instance)
      console.log(`Untracking component: ${componentName}, remaining instances: ${this.componentInstances.get(componentName).size}`)
    }
  }

  // Track fetch requests
  trackFetch(requestId, abortController) {
    this.fetchRequests.add({ requestId, abortController, timestamp: Date.now() })
    console.log(`Tracking fetch request: ${requestId}, total active: ${this.fetchRequests.size}`)
  }

  // Clean up fetch requests
  cleanupFetch(requestId) {
    for (const request of this.fetchRequests) {
      if (request.requestId === requestId) {
        this.fetchRequests.delete(request)
        console.log(`Cleaned up fetch request: ${requestId}, remaining: ${this.fetchRequests.size}`)
        break
      }
    }
  }

  // Abort all pending requests
  abortAllRequests() {
    console.log(`Aborting ${this.fetchRequests.size} pending requests`)
    for (const request of this.fetchRequests) {
      if (request.abortController) {
        request.abortController.abort()
      }
    }
    this.fetchRequests.clear()
  }

  // Track timers
  trackTimer(timerId) {
    this.timers.add(timerId)
    console.log(`Tracking timer: ${timerId}, total active: ${this.timers.size}`)
  }

  // Clean up timer
  cleanupTimer(timerId) {
    this.timers.delete(timerId)
    console.log(`Cleaned up timer: ${timerId}, remaining: ${this.timers.size}`)
  }

  // Clear all timers
  clearAllTimers() {
    console.log(`Clearing ${this.timers.size} active timers`)
    for (const timerId of this.timers) {
      clearTimeout(timerId)
      clearInterval(timerId)
    }
    this.timers.clear()
  }

  // Get memory usage report
  getMemoryReport() {
    const report = {
      components: {},
      fetchRequests: this.fetchRequests.size,
      timers: this.timers.size,
      timestamp: new Date().toISOString()
    }

    for (const [componentName, instances] of this.componentInstances) {
      report.components[componentName] = instances.size
    }

    return report
  }

  // Log memory report
  logMemoryReport() {
    const report = this.getMemoryReport()
    console.group('Memory Usage Report')
    console.log('Components:', report.components)
    console.log('Active fetch requests:', report.fetchRequests)
    console.log('Active timers:', report.timers)
    console.log('Timestamp:', report.timestamp)
    console.groupEnd()
  }

  // Clean up everything
  cleanup() {
    console.log('Performing complete memory cleanup')
    this.abortAllRequests()
    this.clearAllTimers()
    this.componentInstances.clear()
    this.eventListeners.clear()
  }
}

// Create global instance
const memoryTracker = new MemoryTracker()

// Enhanced fetch wrapper with automatic cleanup
export const safeFetch = async (url, options = {}) => {
  const requestId = `fetch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  const abortController = new AbortController()
  
  // Merge abort signal with existing options
  const enhancedOptions = {
    ...options,
    signal: options.signal || abortController.signal
  }

  memoryTracker.trackFetch(requestId, abortController)

  try {
    const response = await fetch(url, enhancedOptions)
    memoryTracker.cleanupFetch(requestId)
    return response
  } catch (error) {
    memoryTracker.cleanupFetch(requestId)
    throw error
  }
}

// Enhanced timer functions
export const safeSetTimeout = (callback, delay) => {
  const timerId = setTimeout(() => {
    memoryTracker.cleanupTimer(timerId)
    callback()
  }, delay)
  memoryTracker.trackTimer(timerId)
  return timerId
}

export const safeSetInterval = (callback, interval) => {
  const timerId = setInterval(callback, interval)
  memoryTracker.trackTimer(timerId)
  return timerId
}

export const safeClearTimeout = (timerId) => {
  clearTimeout(timerId)
  memoryTracker.cleanupTimer(timerId)
}

export const safeClearInterval = (timerId) => {
  clearInterval(timerId)
  memoryTracker.cleanupTimer(timerId)
}

// Vue mixin for automatic memory tracking
export const memoryTrackingMixin = {
  beforeCreate() {
    memoryTracker.trackComponent(this.$options.name || 'UnnamedComponent', this)
  },
  beforeUnmount() {
    memoryTracker.untrackComponent(this.$options.name || 'UnnamedComponent', this)
  }
}

// Global memory tracker instance
export default memoryTracker

// Development helpers
if (process.env.NODE_ENV === 'development') {
  // Make memory tracker available globally for debugging
  window.memoryTracker = memoryTracker
  
  // Log memory report every 30 seconds in development
  setInterval(() => {
    memoryTracker.logMemoryReport()
  }, 30000)
  
  // Clean up on page unload
  window.addEventListener('beforeunload', () => {
    memoryTracker.cleanup()
  })
}
