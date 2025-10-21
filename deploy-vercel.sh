#!/bin/bash

###############################################################################
# Vercel Deployment Script
# Agent Marketplace Platform - Automated Deployment
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

###############################################################################
# Pre-flight Checks
###############################################################################

print_header "Pre-flight Checks"

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm installed: $NPM_VERSION"
else
    print_error "npm not found"
    exit 1
fi

# Check Git
if command_exists git; then
    GIT_VERSION=$(git --version)
    print_success "Git installed: $GIT_VERSION"
else
    print_error "Git not found"
    exit 1
fi

# Check if in correct directory
if [ ! -d "frontend" ]; then
    print_error "frontend directory not found. Please run this script from the project root."
    exit 1
fi

print_success "All pre-flight checks passed"
echo ""

###############################################################################
# Install Vercel CLI
###############################################################################

print_header "Vercel CLI Setup"

if command_exists vercel; then
    VERCEL_VERSION=$(vercel --version)
    print_success "Vercel CLI already installed: $VERCEL_VERSION"
else
    print_info "Installing Vercel CLI..."
    npm install -g vercel@latest
    print_success "Vercel CLI installed"
fi

echo ""

###############################################################################
# Frontend Setup
###############################################################################

print_header "Frontend Setup"

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_info "Installing frontend dependencies..."
    npm install
    print_success "Dependencies installed"
else
    print_success "Dependencies already installed"
fi

# Build check
print_info "Testing build..."
if npm run build; then
    print_success "Build successful"
else
    print_error "Build failed. Please fix errors before deploying."
    exit 1
fi

cd ..

echo ""

###############################################################################
# Environment Configuration
###############################################################################

print_header "Environment Configuration"

# Check if .env.local exists
if [ ! -f "frontend/.env.local" ]; then
    print_warning ".env.local not found"
    print_info "Creating .env.local from example..."
    
    cat > frontend/.env.local << EOF
# Local Environment Variables
# Update these values before deploying

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Stripe Configuration (use test keys for local)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=
NEXT_PUBLIC_SENTRY_DSN=

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
EOF
    
    print_success "Created .env.local"
    print_warning "Please update .env.local with your actual values"
else
    print_success ".env.local exists"
fi

echo ""

###############################################################################
# Deployment Options
###############################################################################

print_header "Deployment Options"

echo "Choose deployment method:"
echo "1) Deploy to Production (vercel --prod)"
echo "2) Deploy to Preview (vercel)"
echo "3) Link Project (first time setup)"
echo "4) Configure Environment Variables"
echo "5) Exit"
echo ""

read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        print_header "Deploying to Production"
        
        print_warning "This will deploy to production. Are you sure? (y/n)"
        read -p "> " confirm
        
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            cd frontend
            print_info "Deploying to production..."
            vercel --prod
            print_success "Deployment complete!"
            cd ..
        else
            print_info "Deployment cancelled"
        fi
        ;;
        
    2)
        print_header "Deploying to Preview"
        
        cd frontend
        print_info "Deploying to preview..."
        vercel
        print_success "Preview deployment complete!"
        cd ..
        ;;
        
    3)
        print_header "Linking Project"
        
        cd frontend
        print_info "Linking to Vercel project..."
        vercel link
        print_success "Project linked!"
        cd ..
        ;;
        
    4)
        print_header "Configure Environment Variables"
        
        cd frontend
        
        echo "Enter environment (production/preview/development):"
        read -p "> " env
        
        echo "Enter NEXT_PUBLIC_API_URL:"
        read -p "> " api_url
        vercel env add NEXT_PUBLIC_API_URL "$env" <<< "$api_url"
        
        echo "Enter NEXT_PUBLIC_WS_URL:"
        read -p "> " ws_url
        vercel env add NEXT_PUBLIC_WS_URL "$env" <<< "$ws_url"
        
        echo "Enter NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY:"
        read -p "> " stripe_key
        vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY "$env" <<< "$stripe_key"
        
        print_success "Environment variables configured!"
        cd ..
        ;;
        
    5)
        print_info "Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""

###############################################################################
# Post-Deployment
###############################################################################

print_header "Post-Deployment Checklist"

echo "✓ Verify deployment at your Vercel URL"
echo "✓ Test API connectivity"
echo "✓ Test WebSocket connection"
echo "✓ Verify authentication flow"
echo "✓ Test agent execution"
echo "✓ Check analytics integration"
echo "✓ Monitor error rates"
echo ""

print_success "Deployment script complete!"

echo ""
print_info "Next steps:"
echo "  1. Visit your Vercel dashboard: https://vercel.com/dashboard"
echo "  2. Configure custom domain (if needed)"
echo "  3. Enable analytics and monitoring"
echo "  4. Set up alerts"
echo ""

print_info "Documentation:"
echo "  - Deployment Guide: VERCEL_DEPLOYMENT.md"
echo "  - Full System Report: FULL_SYSTEM_DEVELOPMENT_REPORT.md"
echo "  - Enterprise Improvements: ENTERPRISE_IMPROVEMENTS.md"
echo ""

print_success "Happy deploying! 🚀"

