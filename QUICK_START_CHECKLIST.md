# ⚡ Quick Start Checklist - InventoryPro

## 🎯 Get Your System Running in 15 Minutes

### ✅ Prerequisites Check
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed (`git --version`)
- [ ] Terminal/Command Prompt access

---

## 🚀 Step 1: Download & Setup (5 minutes)

### 1.1 Create Project Directory
```bash
mkdir inventory-system
cd inventory-system
```

### 1.2 Get the Code
```bash
# Option A: Download from provided files
# Copy the backend and frontend folders to your directory

# Option B: Clone if using Git
# git clone [repository-url]
```

### 1.3 Verify Structure
```
inventory-system/
├── backend/
└── frontend/
```

---

## 🔧 Step 2: Backend Setup (5 minutes)

### 2.1 Navigate to Backend
```bash
cd backend
```

### 2.2 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Start Backend
```bash
python src/main.py
```

**✅ Success Check**: See "Running on http://127.0.0.1:5000"

---

## 🎨 Step 3: Frontend Setup (5 minutes)

### 3.1 Open New Terminal
Keep backend running, open new terminal

### 3.2 Navigate to Frontend
```bash
cd frontend
```

### 3.3 Install Dependencies
```bash
npm install
```

### 3.4 Start Frontend
```bash
npm run dev
```

**✅ Success Check**: See "Local: http://localhost:3000"

---

## 🌐 Step 4: Test Your System

### 4.1 Open Browser
Visit: `http://localhost:3000`

### 4.2 Create Organization
1. Click "Sign up"
2. Fill organization details
3. Create admin account
4. Submit form

### 4.3 Explore Features
- [ ] Dashboard with charts
- [ ] Add products
- [ ] Create warehouses
- [ ] Record inventory movements
- [ ] View reports

---

## 🚨 Troubleshooting

### Backend Issues:
```bash
# Port 5000 in use?
netstat -ano | findstr :5000  # Windows
lsof -ti:5000 | xargs kill    # macOS/Linux

# Dependencies missing?
pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend Issues:
```bash
# Node modules issues?
rm -rf node_modules package-lock.json
npm install

# Port 3000 in use?
npm run dev -- --port 3001
```

### Database Issues:
```bash
# Reset database
rm backend/database/app.db
# Restart backend - database will recreate
```

---

## 🎯 Production Deployment

### Quick Production Setup:
1. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Copy to Backend**:
   ```bash
   cp -r dist/* ../backend/src/static/
   ```

3. **Run Integrated**:
   ```bash
   cd ../backend
   python src/main.py
   ```

4. **Access**: `http://localhost:5000`

---

## 📞 Need Help?

### Common Solutions:
1. **"Python not found"** → Add Python to PATH
2. **"npm not found"** → Install Node.js
3. **"Permission denied"** → Use sudo/admin rights
4. **"Port in use"** → Kill process or use different port
5. **"Module not found"** → Reinstall dependencies

### Check These First:
- [ ] Virtual environment activated (see `(venv)` in terminal)
- [ ] All dependencies installed successfully
- [ ] No error messages in terminal
- [ ] Firewall not blocking ports 3000/5000

---

## 🎉 Success!

When everything works, you should see:
- ✅ Beautiful login page at `http://localhost:3000`
- ✅ API responding at `http://localhost:5000/api/health`
- ✅ Registration form working
- ✅ Dashboard with charts and data

**You're ready to manage inventory like a pro!** 🚀

---

## 📋 Next Steps

1. **Customize branding** (colors, logo, company name)
2. **Add your products** and categories
3. **Set up warehouses** for your locations
4. **Import existing inventory** data
5. **Train your team** on the system
6. **Deploy to production** server

**Happy inventory managing!** 📦✨

