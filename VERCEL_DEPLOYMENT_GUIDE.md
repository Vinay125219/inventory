# 🚀 Vercel Deployment Guide - InventoryPro

## 📋 Overview

This guide provides step-by-step instructions for deploying InventoryPro to Vercel, including both frontend-only and full-stack deployment options.

---

## 🎯 Deployment Options

### Option 1: Frontend-Only (Static Demo)
- **Best for**: Demos, portfolios, testing
- **Pros**: Free, fast, simple
- **Cons**: No backend functionality, demo data only

### Option 2: Full-Stack (Production Ready)
- **Best for**: Production use, real businesses
- **Pros**: Complete functionality, real database
- **Cons**: Requires backend hosting (additional cost)

---

## 🌐 Option 1: Frontend-Only Deployment

### Step 1: Prepare the Frontend

#### 1.1 Navigate to Frontend Directory
```bash
cd inventory-management-frontend
```

#### 1.2 Install Dependencies
```bash
npm install
```

#### 1.3 Configure for Static Demo
Create/update `.env` file:
```env
VITE_API_URL=demo
VITE_APP_NAME=InventoryPro
VITE_DEMO_MODE=true
```

#### 1.4 Update API Client for Demo Mode
Edit `src/lib/api.js` to add demo mode:
```javascript
// Add at the top of api.js
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

// Mock data for demo
const DEMO_DATA = {
  organizations: [
    { id: 1, name: "Demo Company", email: "demo@company.com" }
  ],
  users: [
    { id: 1, username: "demo", email: "demo@company.com", first_name: "Demo", last_name: "User" }
  ],
  products: [
    { id: 1, name: "Laptop Pro 15\"", sku: "LP001", category: "Electronics", price: 1299.99, stock: 25 },
    { id: 2, name: "Wireless Mouse", sku: "WM001", category: "Accessories", price: 29.99, stock: 150 },
    // Add more demo products...
  ]
};

// Modify API functions to return demo data when in demo mode
export const apiClient = {
  async get(endpoint) {
    if (DEMO_MODE) {
      // Return appropriate demo data based on endpoint
      return { data: DEMO_DATA };
    }
    // Original API logic...
  },
  // ... other methods
};
```

#### 1.5 Build for Production
```bash
npm run build
```

### Step 2: Deploy to Vercel

#### 2.1 Install Vercel CLI
```bash
npm install -g vercel
```

#### 2.2 Login to Vercel
```bash
vercel login
```

#### 2.3 Deploy
```bash
# From the frontend directory
vercel --prod

# Follow the prompts:
# ? Set up and deploy "inventory-management-frontend"? [Y/n] y
# ? Which scope do you want to deploy to? [Your Account]
# ? Link to existing project? [y/N] n
# ? What's your project's name? inventory-pro
# ? In which directory is your code located? ./
```

#### 2.4 Configure Build Settings
If prompted, use these settings:
- **Framework Preset**: Vite
- **Root Directory**: `./`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Step 3: Configure Environment Variables

#### 3.1 Via Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add:
   - `VITE_API_URL` = `demo`
   - `VITE_APP_NAME` = `InventoryPro`
   - `VITE_DEMO_MODE` = `true`

#### 3.2 Via CLI
```bash
vercel env add VITE_API_URL
# Enter: demo

vercel env add VITE_APP_NAME
# Enter: InventoryPro

vercel env add VITE_DEMO_MODE
# Enter: true
```

### Step 4: Redeploy with Environment Variables
```bash
vercel --prod
```

---

## 🔧 Option 2: Full-Stack Deployment

### Step 1: Deploy Backend

#### Option A: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Navigate to backend
cd inventory-management-backend

# Login and deploy
railway login
railway init
railway up
```

#### Option B: Heroku
```bash
# Install Heroku CLI
# Create Procfile in backend directory
echo "web: python src/main.py" > Procfile

# Deploy
heroku create your-inventory-backend
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### Option C: DigitalOcean App Platform
1. Connect your GitHub repository
2. Select the backend directory
3. Configure build settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python src/main.py`

### Step 2: Configure Backend Environment Variables

#### For Railway:
```bash
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=your-super-secret-key-here
railway variables set JWT_SECRET_KEY=your-jwt-secret-key-here
railway variables set DATABASE_URL=postgresql://user:pass@host:port/db
```

#### For Heroku:
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set JWT_SECRET_KEY=your-jwt-secret-key-here
```

### Step 3: Deploy Frontend to Vercel

#### 3.1 Update Frontend Configuration
```bash
cd inventory-management-frontend
```

Create `.env.production`:
```env
VITE_API_URL=https://your-backend-url.railway.app/api
VITE_APP_NAME=InventoryPro
VITE_DEMO_MODE=false
```

#### 3.2 Build and Deploy
```bash
npm run build
vercel --prod
```

#### 3.3 Configure Vercel Environment Variables
```bash
vercel env add VITE_API_URL
# Enter: https://your-backend-url.railway.app/api

vercel env add VITE_APP_NAME
# Enter: InventoryPro

vercel env add VITE_DEMO_MODE
# Enter: false
```

---

## ⚙️ Advanced Vercel Configuration

### Custom Domain Setup

#### 1. Add Domain in Vercel Dashboard
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

#### 2. SSL Certificate
Vercel automatically provides SSL certificates for custom domains.

### Performance Optimization

#### 1. Create `vercel.json` in Frontend Root
```json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "functions": {
    "app/api/**/*.js": {
      "runtime": "nodejs18.x"
    }
  },
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/",
      "destination": "/login",
      "permanent": false
    }
  ]
}
```

#### 2. Optimize Build Settings
```json
// In package.json
{
  "scripts": {
    "build": "vite build --mode production",
    "preview": "vite preview"
  }
}
```

---

## 🔒 Security Configuration

### Environment Variables Security
```bash
# Never commit these to Git
echo ".env*" >> .gitignore
echo "*.local" >> .gitignore
```

### CORS Configuration for Production
Update backend `main.py`:
```python
from flask_cors import CORS

# Configure CORS for production
CORS(app, origins=[
    "https://your-frontend-domain.vercel.app",
    "https://your-custom-domain.com"
])
```

### Content Security Policy
Add to `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        }
      ]
    }
  ]
}
```

---

## 📊 Monitoring & Analytics

### Vercel Analytics
```bash
# Install Vercel Analytics
npm install @vercel/analytics

# Add to main.tsx
import { Analytics } from '@vercel/analytics/react';

function App() {
  return (
    <>
      <YourApp />
      <Analytics />
    </>
  );
}
```

### Performance Monitoring
```json
// In vercel.json
{
  "functions": {
    "app/**/*.js": {
      "runtime": "nodejs18.x",
      "memory": 1024
    }
  }
}
```

---

## 🚨 Troubleshooting

### Common Deployment Issues

#### 1. Build Failures
```bash
# Check build locally first
npm run build

# Check for missing dependencies
npm install

# Clear cache
rm -rf node_modules package-lock.json
npm install
```

#### 2. Environment Variable Issues
```bash
# List current variables
vercel env ls

# Remove incorrect variables
vercel env rm VARIABLE_NAME

# Add correct variables
vercel env add VARIABLE_NAME
```

#### 3. CORS Errors
- Ensure backend CORS is configured for your Vercel domain
- Check that API URLs are correct
- Verify environment variables are set

#### 4. 404 Errors on Refresh
Add to `vercel.json`:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Debugging Commands
```bash
# View deployment logs
vercel logs

# Check function logs
vercel logs --follow

# Inspect deployment
vercel inspect [deployment-url]
```

---

## 📈 Scaling Considerations

### Database Scaling
- **Development**: SQLite (included)
- **Production**: PostgreSQL (recommended)
- **Enterprise**: MongoDB or MySQL

### CDN and Caching
Vercel automatically provides:
- Global CDN
- Edge caching
- Image optimization
- Automatic compression

### Performance Optimization
```javascript
// Lazy loading components
const Dashboard = lazy(() => import('./components/dashboard/Dashboard'));
const Products = lazy(() => import('./components/products/ProductsPage'));

// Code splitting
const routes = [
  {
    path: '/dashboard',
    component: lazy(() => import('./pages/Dashboard'))
  }
];
```

---

## 💰 Cost Estimation

### Vercel Pricing (Frontend)
- **Hobby Plan**: Free
  - 100GB bandwidth
  - 1000 serverless function invocations
  - Perfect for demos and small projects

- **Pro Plan**: $20/month
  - 1TB bandwidth
  - Unlimited serverless functions
  - Custom domains
  - Analytics

### Backend Hosting Costs
- **Railway**: $5-20/month
- **Heroku**: $7-25/month
- **DigitalOcean**: $5-15/month

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Test application locally
- [ ] Build frontend successfully
- [ ] Configure environment variables
- [ ] Update API URLs
- [ ] Test responsive design
- [ ] Check console for errors

### Deployment
- [ ] Deploy backend (if full-stack)
- [ ] Configure backend environment variables
- [ ] Deploy frontend to Vercel
- [ ] Configure frontend environment variables
- [ ] Test deployed application
- [ ] Configure custom domain (optional)

### Post-Deployment
- [ ] Test all functionality
- [ ] Check performance metrics
- [ ] Set up monitoring
- [ ] Configure analytics
- [ ] Document deployment URLs
- [ ] Share with stakeholders

---

## 🎉 Success!

After successful deployment, you'll have:

1. **Live Application**: Accessible via Vercel URL
2. **Custom Domain**: (Optional) Your branded URL
3. **SSL Certificate**: Automatic HTTPS
4. **Global CDN**: Fast loading worldwide
5. **Automatic Deployments**: Git-based deployments
6. **Performance Monitoring**: Built-in analytics

**Your inventory management system is now live and ready for users!** 🚀

---

## 📞 Support

### Vercel Resources
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [Vercel Support](https://vercel.com/support)

### Project Support
- Check the included documentation files
- Review error logs in Vercel dashboard
- Test locally before deploying
- Verify environment variables

**Happy deploying!** ✨

