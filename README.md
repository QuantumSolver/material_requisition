## Material Requisition System

A simplified, visual material requisition system built with Frappe and Doppio framework, specifically designed for construction workers and non-technical users.

## Features

### 🎯 User-Friendly Interface
- **Visual Item Selection**: Picture-based material selection with icons and images
- **Large Interactive Elements**: Touch-friendly buttons and controls
- **Color-Coded Status System**: Easy-to-understand visual status indicators
- **Mobile Responsive**: Works seamlessly on tablets and mobile devices

### 🚀 Simplified Workflow
- **One-Click Material Requests**: Streamlined request creation process
- **Hidden Administrative Fields**: Complex fields are hidden from primary interface
- **Direct Purchase Order Creation**: Create POs directly from material requests
- **Single-Step Submission**: Simplified "Submit" workflow

### 📊 Dashboard & Analytics
- **Status Overview Cards**: Visual representation of pending, ordered, partial, and received requests
- **Recent Requests**: Quick access to latest material requests
- **Real-time Updates**: Live status updates and notifications

## Technology Stack

- **Frontend**: Vue 3 + TypeScript + TailwindCSS
- **Backend**: Frappe Framework (Python)
- **UI Components**: Lucide Icons + Headless UI
- **Build Tool**: Vite
- **Integration**: Doppio Framework for SPA integration

## Quick Start

### Access the System
Navigate to `http://your-site/promep` to access the Material Requisition System.

### Creating Your First Request
1. Click the large "Create Material Requisition" button
2. Select materials using the visual item selector
3. Adjust quantities and submit

## Development Setup

### Prerequisites
- Frappe Bench setup
- Node.js and npm/yarn
- Python 3.8+

### Installation
```bash
# Install Doppio Framework
bench get-app https://github.com/NagariaHussain/doppio
bench --site [your-site] install-app doppio

# Install Material Requisition App
bench --site [your-site] install-app material_requisition

# Build Frontend Assets
cd apps/material_requisition/Promep
npm install && npm run build
cd ../../.. && bench build --app material_requisition
```

## API Endpoints

- **Dashboard**: `/api/method/material_requisition.api.dashboard.get_dashboard_data`
- **Items**: `/api/method/material_requisition.api.material_request.get_visual_items`
- **Create Request**: `/api/method/material_requisition.api.material_request.create_simplified_material_request`

## License

AGPL-3.0

---

**Built with ❤️ for construction teams who deserve better tools.**

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app material_requisition
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/material_requisition
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

agpl-3.0
