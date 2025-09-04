# Supabase Google OAuth Setup Guide for Team Development

## Quick Setup for New Team Members

### 1. Environment Configuration
After cloning the repository, create your local environment file:

```bash
cd frontend
cp .env.example .env.local
```

### 2. Update Your .env.local File
Replace the placeholder values in `.env.local` with your actual Supabase credentials:

```env
# Supabase Configuration (Required for Google OAuth)
NEXT_PUBLIC_SUPABASE_URL=https://okgcbgimqhfvbxagvgez.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rZ2NiZ2ltcWhmdmJ4YWd2Z2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5NTMyNTQsImV4cCI6MjA3MjUyOTI1NH0.4LrZfM-dnClOr7sO4VoOxFiBhmqZq1H9YSQgagCfXAc
```

### 3. Install Dependencies
```bash
npm install
```

### 4. Start Development Server
```bash
npm run dev
```

## Repository Deployment Checklist

### ✅ What's Already Configured
- [x] `.env.example` with placeholder values
- [x] `.gitignore` excludes `.env.local` files
- [x] Supabase client configuration
- [x] Google OAuth implementation
- [x] Professional auth callback UI

### ⚠️ Important Notes
1. **Never commit `.env.local`** - It's already in `.gitignore`
2. **Always use `.env.example`** - Update it when adding new environment variables
3. **Supabase credentials are shared** - Same project for all team members

## Environment Variables Explained

### Required for Google OAuth
- `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous/public key (safe to expose)

### Security Notes
- The `NEXT_PUBLIC_` prefix makes these variables available in the browser
- The anon key is designed to be public and has restricted permissions
- Actual authentication happens server-side through Supabase

## Troubleshooting

### Common Issues After Clone
1. **"Supabase client not configured"**
   - Ensure `.env.local` exists with correct values
   - Restart the development server

2. **Google OAuth redirect errors**
   - Verify Supabase dashboard has correct redirect URLs
   - Check that localhost:3000 is in allowed origins

3. **Module not found errors**
   - Run `npm install` to install dependencies
   - Clear node_modules and reinstall if needed

## Team Workflow

### For Repository Maintainer
1. Update `.env.example` when adding new environment variables
2. Never commit actual credentials
3. Document any new setup steps in this guide

### For New Team Members
1. Clone repository
2. Copy `.env.example` to `.env.local`
3. Get Supabase credentials from team lead
4. Update `.env.local` with actual values
5. Run `npm install && npm run dev`

## Production Deployment

### Environment Variables to Set
```env
NEXT_PUBLIC_SUPABASE_URL=your-production-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-production-supabase-anon-key
```

### Supabase Configuration for Production
1. Update Site URL in Supabase dashboard
2. Add production domain to redirect URLs
3. Configure Google OAuth for production domain

## Support
If you encounter issues:
1. Check this guide first
2. Verify environment variables are correct
3. Ensure Supabase project is accessible
4. Contact team lead for credentials if needed
