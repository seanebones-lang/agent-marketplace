#!/bin/bash

# Vercel Deployment Script - Fixed Version
# This script will help you deploy your Next.js frontend to Vercel

echo "🚀 Starting Vercel Deployment Process..."

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

# Check if Vercel CLI is available
if ! command -v vercel &> /dev/null; then
    echo "📥 Installing Vercel CLI..."
    npm install -g vercel
fi

echo "🔐 Please login to Vercel..."
vercel login

echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should now be live at the URL provided above."
