import './style.css';
import { createApp, reactive } from "vue";
import App from "./App.vue";
import router from './router';

// Simple implementations for now
const call = async (method, params = {}) => {
  const response = await fetch(`/api/method/${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || ''
    },
    body: JSON.stringify(params)
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  if (data.exc) {
    throw new Error(data.exc);
  }

  return data.message;
};

class SimpleAuth {
  constructor() {
    this.isLoggedIn = false;
    this.user = null;
    this._checkedAuth = false;
    // Don't auto-check auth in constructor to avoid blocking
  }

  async checkAuth() {
    try {
      const response = await fetch('/api/method/frappe.auth.get_logged_user', {
        method: 'GET',
        credentials: 'include', // Include cookies for session
        headers: {
          'Accept': 'application/json',
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.isLoggedIn = data.message && data.message !== 'Guest';
      this.user = data.message;

      console.log('Auth check result:', { isLoggedIn: this.isLoggedIn, user: this.user });

    } catch (error) {
      console.error('Auth check failed:', error);
      this.isLoggedIn = false;
      this.user = null;
    }
  }

  async login(email, password) {
    try {
      const response = await fetch('/api/method/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          usr: email,
          pwd: password
        })
      });

      const data = await response.json();
      if (data.message === 'Logged In') {
        this.isLoggedIn = true;
        this.user = email;
        return true;
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      throw error;
    }
  }

  async logout() {
    try {
      await fetch('/api/method/logout', { method: 'POST' });
      this.isLoggedIn = false;
      this.user = null;
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
}

// Simple global utilities
const globalUtils = {
  install(app) {
    // Add global properties if needed
    app.config.globalProperties.$call = call;
  }
};

const app = createApp(App);
const auth = reactive(new SimpleAuth());

// Plugins
app.use(router);
app.use(globalUtils);

// Global Properties,
// components can inject this
app.provide("$auth", auth);
app.provide("$call", call);


// Configure route guards - simplified for Frappe integration
router.beforeEach(async (to, from, next) => {
	// Check authentication status on first load
	if (!auth.isLoggedIn && !auth._checkedAuth) {
		await auth.checkAuth();
		auth._checkedAuth = true;
	}

	// If user is not logged in, redirect to Frappe login
	if (!auth.isLoggedIn) {
		window.location.href = '/login?redirect-to=' + encodeURIComponent(window.location.pathname + window.location.hash);
		return;
	}

	next();
});

// Add afterEach guard for cleanup
router.afterEach((to, from) => {
	// Clean up after route changes to prevent memory leaks
	console.log(`Route changed from ${from.path} to ${to.path}`);

	// Force garbage collection if available (development only)
	if (window.gc && process.env.NODE_ENV === 'development') {
		setTimeout(() => {
			window.gc();
			console.log('Garbage collection triggered after route change');
		}, 100);
	}

	// Clear any global event listeners or timers that might leak
	// This is a good place to add cleanup for global resources
});

app.mount("#app");
