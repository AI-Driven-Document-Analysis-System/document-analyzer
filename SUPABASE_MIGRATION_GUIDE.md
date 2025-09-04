# Supabase Google OAuth Migration Guide

## Overview
This guide documents the migration from Appwrite to Supabase for Google OAuth authentication, fixing the account selection issues that were present in the previous implementation.

## What Was Fixed
- **Account Selection Issue**: Google OAuth now properly forces account selection instead of automatically using previously signed-in accounts
- **Sign-up vs Sign-in Flow**: Separate flows for sign-up and sign-in with proper consent handling
- **Session Management**: Improved session handling with Supabase's built-in authentication

## Setup Instructions

### 1. Environment Configuration
Create a `.env.local` file in the frontend directory with your Supabase credentials:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://okgcbgimqhfvbxagvgez.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rZ2NiZ2ltcWhmdmJ4YWd2Z2V6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5NTMyNTQsImV4cCI6MjA3MjUyOTI1NH0.4LrZfM-dnClOr7sO4VoOxFiBhmqZq1H9YSQgagCfXAc
```

### 2. Supabase Dashboard Configuration

#### Enable Google OAuth Provider
1. Go to your Supabase project dashboard
2. Navigate to Authentication > Providers
3. Enable Google provider
4. Configure the following settings:

**Google OAuth Settings:**
- **Client ID**: `859880898609-cfi5h8i4v4v238gonouulu4u5vqqjc0v.apps.googleusercontent.com`
- **Client Secret**: [Your Google OAuth Client Secret]
- **Redirect URL**: `https://okgcbgimqhfvbxagvgez.supabase.co/auth/v1/callback`

#### Site URL Configuration
In Authentication > URL Configuration, set:
- **Site URL**: `http://localhost:3000` (for development)
- **Redirect URLs**: 
  - `http://localhost:3000/auth/callback`
  - `http://localhost:3000/auth/callback?mode=signup`

### 3. Google Cloud Console Configuration
Update your Google OAuth consent screen and credentials:

1. Go to Google Cloud Console > APIs & Credentials
2. Update your OAuth 2.0 Client IDs
3. Add these authorized redirect URIs:
   - `https://okgcbgimqhfvbxagvgez.supabase.co/auth/v1/callback`
   - `http://localhost:3000/auth/callback` (for development)

## Implementation Details

### New Files Created
- `src/lib/supabase.ts` - Supabase client configuration
- `src/services/supabaseAuthService.ts` - New Google OAuth service using Supabase
- `.env.example` - Environment configuration template

### Modified Files
- `src/components/auth/auth-modal.tsx` - Updated to use Supabase service with separate sign-in/sign-up flows
- `src/app/auth/callback/page.tsx` - Updated callback handler for Supabase
- `app/api/auth.py` - Backend updated to handle Supabase tokens

### Deprecated Files
- `src/services/googleAuthService.ts` - Marked as deprecated, replaced by supabaseAuthService
- `src/services/appwriteConfig.ts` - Marked as deprecated, replaced by lib/supabase

## Key Features

### 1. Forced Account Selection
```typescript
await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    queryParams: {
      access_type: 'offline',
      prompt: 'select_account', // Forces account selection
    },
  },
});
```

### 2. Separate Sign-up Flow
```typescript
await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: `${window.location.origin}/auth/callback?mode=signup`,
    queryParams: {
      access_type: 'offline',
      prompt: 'consent select_account', // Forces consent and account selection
    },
  },
});
```

### 3. Improved Session Management
- Automatic token refresh
- Persistent sessions
- Proper session detection in URLs

## Testing the Implementation

### 1. Start the Development Server
```bash
cd frontend
npm run dev
```

### 2. Test Sign-in Flow
1. Click "Sign In" in the auth modal
2. Click "Sign in with Google"
3. Verify that Google shows account selection screen
4. Complete authentication
5. Verify redirect to dashboard

### 3. Test Sign-up Flow
1. Click "Sign Up" in the auth modal
2. Click "Sign up with Google"
3. Verify that Google shows consent screen and account selection
4. Complete authentication
5. Verify new user creation

## Cleanup Tasks (After Testing)

Once you've confirmed everything works:

1. **Remove Appwrite Dependencies**
   ```bash
   npm uninstall appwrite
   ```

2. **Delete Deprecated Files**
   - `src/services/googleAuthService.ts`
   - `src/services/appwriteConfig.ts`

3. **Update Package.json**
   Remove any Appwrite-related dependencies

## Troubleshooting

### Common Issues

1. **Environment Variables Not Loading**
   - Ensure `.env.local` is in the frontend root directory
   - Restart the development server after adding environment variables

2. **Google OAuth Redirect Mismatch**
   - Verify redirect URLs in Google Cloud Console match Supabase settings
   - Check that Site URL in Supabase matches your development URL

3. **Session Not Persisting**
   - Clear browser storage and cookies
   - Verify Supabase client configuration

### Debug Information
- Check browser console for authentication errors
- Monitor Supabase dashboard for authentication logs
- Verify backend receives correct user data structure

## Benefits of Migration

1. **Fixed Account Selection**: Users can now properly choose which Google account to use
2. **Better UX**: Separate sign-in and sign-up flows with appropriate consent screens
3. **Improved Reliability**: Supabase's mature authentication system
4. **Better Session Management**: Automatic token refresh and session persistence
5. **Easier Maintenance**: Simplified authentication flow with better error handling

## Support

If you encounter issues:
1. Check the browser console for errors
2. Verify environment variables are correctly set
3. Ensure Supabase and Google Cloud Console configurations match
4. Test with different Google accounts to verify account selection works
