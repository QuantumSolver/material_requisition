/**
 * Test script to verify memory leak fixes
 * Run this in the browser console to test memory management
 */

// Test memory tracking
function testMemoryTracking() {
  console.log('Testing memory tracking...');
  
  // Check if memory tracker is available
  if (typeof window.memoryTracker === 'undefined') {
    console.error('Memory tracker not available. Make sure you are in development mode.');
    return false;
  }
  
  // Get initial memory report
  const initialReport = window.memoryTracker.getMemoryReport();
  console.log('Initial memory report:', initialReport);
  
  return true;
}

// Test fetch cleanup
async function testFetchCleanup() {
  console.log('Testing fetch cleanup...');
  
  try {
    // Import safeFetch (this would normally be done in components)
    const { safeFetch } = await import('./src/utils/memoryUtils.js');
    
    // Make a test request
    const response = await safeFetch('/api/method/frappe.auth.get_logged_user');
    console.log('Fetch test successful:', response.ok);
    
    // Check if request was tracked and cleaned up
    const report = window.memoryTracker.getMemoryReport();
    console.log('Fetch requests after test:', report.fetchRequests);
    
    return true;
  } catch (error) {
    console.error('Fetch test failed:', error);
    return false;
  }
}

// Test component navigation memory usage
function testNavigationMemory() {
  console.log('Testing navigation memory usage...');
  
  const initialReport = window.memoryTracker.getMemoryReport();
  console.log('Before navigation:', initialReport);
  
  // Navigate to create-request
  if (window.location.hash !== '#/create-request') {
    window.location.hash = '#/create-request';
    
    setTimeout(() => {
      const afterNavReport = window.memoryTracker.getMemoryReport();
      console.log('After navigation to create-request:', afterNavReport);
      
      // Navigate back
      window.location.hash = '#/';
      
      setTimeout(() => {
        const finalReport = window.memoryTracker.getMemoryReport();
        console.log('After navigation back to home:', finalReport);
        
        // Check if components were properly cleaned up
        const createRequestInstances = finalReport.components.CreateRequest || 0;
        const itemSelectorInstances = finalReport.components.ItemSelector || 0;
        
        if (createRequestInstances === 0 && itemSelectorInstances === 0) {
          console.log('✅ Navigation memory test PASSED - components properly cleaned up');
        } else {
          console.log('❌ Navigation memory test FAILED - components still in memory');
        }
      }, 1000);
    }, 1000);
  }
}

// Test timer cleanup
function testTimerCleanup() {
  console.log('Testing timer cleanup...');
  
  // This would normally be imported in components
  const testTimer = setTimeout(() => {
    console.log('Test timer executed');
  }, 5000);
  
  // Simulate component cleanup
  clearTimeout(testTimer);
  
  console.log('Timer cleanup test completed');
}

// Run all tests
async function runAllTests() {
  console.group('Memory Leak Fix Tests');
  
  const tests = [
    { name: 'Memory Tracking', test: testMemoryTracking },
    { name: 'Fetch Cleanup', test: testFetchCleanup },
    { name: 'Timer Cleanup', test: testTimerCleanup }
  ];
  
  for (const { name, test } of tests) {
    console.group(name);
    try {
      const result = await test();
      console.log(result ? '✅ PASSED' : '❌ FAILED');
    } catch (error) {
      console.error('❌ FAILED with error:', error);
    }
    console.groupEnd();
  }
  
  // Run navigation test separately as it requires user interaction
  console.group('Navigation Memory Test');
  console.log('This test requires manual navigation. Run testNavigationMemory() separately.');
  console.groupEnd();
  
  console.groupEnd();
  
  // Final memory report
  if (window.memoryTracker) {
    window.memoryTracker.logMemoryReport();
  }
}

// Make functions available globally for manual testing
window.testMemoryFixes = {
  runAllTests,
  testMemoryTracking,
  testFetchCleanup,
  testNavigationMemory,
  testTimerCleanup
};

console.log('Memory leak test functions loaded. Run window.testMemoryFixes.runAllTests() to start testing.');

// Auto-run tests if this script is executed directly
if (typeof window !== 'undefined' && window.location) {
  // Wait for app to load
  setTimeout(() => {
    runAllTests();
  }, 2000);
}
