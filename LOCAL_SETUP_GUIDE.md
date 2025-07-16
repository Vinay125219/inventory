# InventoryPro - Local Environment Setup Guide

## Complete Inventory Management System Setup

This guide will help you set up the InventoryPro inventory management system on your local PC with detailed version requirements and verification steps.

## 🎯 System Overview

**InventoryPro** is a comprehensive inventory management system featuring:
- **Backend**: Flask (Python) with SQLite database
- **Frontend**: React with modern UI/UX design
- **Features**: Multi-client support, real-time inventory tracking, analytics, reporting
- **Architecture**: RESTful API with JWT authentication

---

## 📋 Prerequisites & Version Requirements

### 1. Python Installation
**Required Version**: Python 3.8 or higher (Recommended: Python 3.11)

#### Windows:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Choose "Customize installation" and ensure pip is included

#### macOS:
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

#### ✅ Verification:
```bash
python --version
# Should show: Python 3.8.x or higher

pip --version
# Should show: pip 21.x.x or higher
```

### 2. Node.js Installation
**Required Version**: Node.js 18.x or higher (Recommended: Node.js 20.x)

#### Windows/macOS:
1. Download from [nodejs.org](https://nodejs.org/)
2. Install the LTS version
3. npm is included automatically

#### Linux:
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### ✅ Verification:
```bash
node --version
# Should show: v18.x.x or higher

npm --version
# Should show: 9.x.x or higher
```

### 3. Git Installation
**Required**: Git 2.x or higher

#### Windows:
Download from [git-scm.com](https://git-scm.com/)

#### macOS:
```bash
brew install git
# Or use Xcode Command Line Tools
xcode-select --install
```

#### Linux:
```bash
sudo apt install git
```

#### ✅ Verification:
```bash
git --version
# Should show: git version 2.x.x
```

---

## 🚀 Step-by-Step Setup Instructions

### Step 1: Create Project Directory
```bash
# Create main project directory
mkdir inventory-management-system
cd inventory-management-system

# Verify you're in the right directory
pwd
```

**✅ Verification**: You should see the full path to your project directory.

### Step 2: Backend Setup (Flask)

#### 2.1 Create Backend Directory
```bash
# Create backend directory structure
mkdir backend
cd backend
```

#### 2.2 Create Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

**✅ Verification**: Your command prompt should show `(venv)` at the beginning.

#### 2.3 Create Requirements File
Create `requirements.txt` in the backend directory:
```txt
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.7.1
Flask-CORS==6.0.0
bcrypt==4.3.0
python-dateutil==2.9.0
Werkzeug==3.1.3
```

#### 2.4 Install Python Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**✅ Verification**: You should see all packages listed with their versions.

#### 2.5 Create Backend Files
Create the following directory structure in `backend/`:
```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── inventory.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── inventory.py
│       └── reports.py
├── database/
├── requirements.txt
└── venv/
```

Copy the backend files from the system I built (I'll provide them in the next step).

#### 2.6 Test Backend
```bash
# Run the Flask application
python src/main.py

# You should see:
# * Running on http://127.0.0.1:5000
```

**✅ Verification**: Open browser to `http://localhost:5000/api/health` - should return JSON with status "healthy".

### Step 3: Frontend Setup (React)

#### 3.1 Create Frontend Directory
```bash
# Go back to main project directory
cd ..

# Create React application
npx create-react-app frontend
cd frontend
```

#### 3.2 Install Additional Dependencies
```bash
# Install required packages
npm install react-router-dom framer-motion lucide-react recharts

# Install UI components and styling
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select
npm install @radix-ui/react-tabs @radix-ui/react-switch @radix-ui/react-avatar
npm install @radix-ui/react-label @radix-ui/react-separator @radix-ui/react-progress
npm install tailwindcss @tailwindcss/forms class-variance-authority clsx tailwind-merge

# Install development dependencies
npm install -D @types/node
```

#### 3.3 Setup Tailwind CSS
```bash
# Initialize Tailwind CSS
npx tailwindcss init -p
```

Update `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

#### 3.4 Update Package.json Scripts
Add to `package.json`:
```json
{
  "scripts": {
    "dev": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

#### 3.5 Test Frontend
```bash
# Start development server
npm run dev

# You should see:
# Local:   http://localhost:3000
```

**✅ Verification**: Open browser to `http://localhost:3000` - should show React app.

### Step 4: Integration Setup

#### 4.1 Configure API Proxy
In `frontend/package.json`, add:
```json
{
  "name": "frontend",
  "proxy": "http://localhost:5000",
  "dependencies": {
    ...
  }
}
```

#### 4.2 Environment Variables
Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_NAME=InventoryPro
```

Create `backend/.env`:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-string-change-in-production
DATABASE_URL=sqlite:///database/app.db
```

---

## 🔧 Development Workflow

### Starting the Application

#### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python src/main.py
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### ✅ Final Verification Checklist

1. **Backend Health Check**:
   - Visit: `http://localhost:5000/api/health`
   - Should return: `{"status": "healthy", "message": "Inventory Management System API is running"}`

2. **Frontend Loading**:
   - Visit: `http://localhost:3000`
   - Should show: InventoryPro login page with beautiful UI

3. **API Integration**:
   - Try registering a new organization
   - Check browser network tab for API calls to backend

4. **Database Creation**:
   - Check `backend/database/app.db` file exists after first API call

---

## 🎨 Features Overview

### ✨ What You Get:

1. **Authentication System**:
   - Multi-organization support
   - JWT-based authentication
   - Role-based access control

2. **Inventory Management**:
   - Product catalog management
   - Real-time stock tracking
   - Warehouse management
   - Movement history

3. **Analytics & Reporting**:
   - Interactive dashboards
   - Inventory value trends
   - Low stock alerts
   - Movement analysis

4. **Modern UI/UX**:
   - Responsive design
   - Beautiful animations
   - Dark/light theme support
   - Mobile-friendly interface

### 🔧 Technical Stack:

**Backend**:
- Flask 3.1.1 (Python web framework)
- SQLAlchemy (Database ORM)
- JWT Extended (Authentication)
- Flask-CORS (Cross-origin requests)
- SQLite (Database)

**Frontend**:
- React 18+ (UI framework)
- React Router (Navigation)
- Framer Motion (Animations)
- Tailwind CSS (Styling)
- Recharts (Data visualization)
- Lucide React (Icons)

---

## 🚨 Troubleshooting

### Common Issues:

1. **Python not found**:
   ```bash
   # Windows: Add Python to PATH
   # Check: python --version
   ```

2. **npm command not found**:
   ```bash
   # Install Node.js from nodejs.org
   # Check: node --version && npm --version
   ```

3. **Port already in use**:
   ```bash
   # Kill process on port 5000
   # Windows: netstat -ano | findstr :5000
   # macOS/Linux: lsof -ti:5000 | xargs kill
   ```

4. **CORS errors**:
   - Ensure Flask-CORS is installed
   - Check proxy configuration in package.json

5. **Database errors**:
   - Delete `backend/database/app.db` and restart backend
   - Check file permissions

### Getting Help:

1. **Check logs**: Both terminal windows for error messages
2. **Browser console**: F12 → Console tab for frontend errors
3. **Network tab**: F12 → Network tab for API call issues

---

## 🎯 Next Steps

After successful setup:

1. **Create your first organization** using the registration form
2. **Add warehouses** to organize your inventory
3. **Create product categories** for better organization
4. **Add products** to your catalog
5. **Record inventory movements** to track stock
6. **Explore reports** and analytics features

---

## 📞 Support

If you encounter any issues during setup:

1. **Double-check versions** of Python, Node.js, and npm
2. **Verify all dependencies** are installed correctly
3. **Check firewall/antivirus** settings if ports are blocked
4. **Review error messages** carefully for specific issues

The system is designed to be production-ready and can handle multiple clients and users simultaneously. Enjoy your new inventory management system! 🎉

