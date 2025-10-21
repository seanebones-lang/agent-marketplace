#!/bin/bash

# Direct Frontend Deployment Script
# This script deploys the frontend as a separate Vercel project

echo "🚀 Deploying Frontend Directly to Vercel..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo "📦 Installing dependencies..."
npm install

echo "🔧 Building the application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please fix the errors above before deploying."
    exit 1
fi

echo "✅ Build successful!"

echo "🔐 Please login to Vercel..."
echo "This will open a browser window for authentication."
npx vercel login

echo "🚀 Deploying to Vercel..."
echo "When prompted:"
echo "  - Set up and deploy? Y"
echo "  - Which scope? (select your account)"
echo "  - Link to existing project? N (create new)"
echo "  - Project name: agent-marketplace-frontend"
echo "  - Directory: ./"
echo "  - Override settings? N"
echo ""

npx vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should now be live at the URL provided above."
