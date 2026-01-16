# Fix Redirect URI Mismatch Error

## Error: `redirect_uri_mismatch`

This error means the redirect URI in Google Cloud Console doesn't match what django-allauth is sending.

## ✅ Fixed Configuration

I've updated your Site configuration. Now you need to add the correct redirect URI in Google Cloud Console.

## Step-by-Step Fix

### 1. Go to Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**

### 2. Edit Your OAuth 2.0 Client

1. Find your OAuth 2.0 Client ID (from your `.env` file)
2. Click on it to edit

### 3. Add Authorized Redirect URI

In the **Authorized redirect URIs** section, click **+ ADD URI** and add:

```
http://localhost:8000/accounts/google/login/callback/
```

**⚠️ CRITICAL:**
- Must include the trailing slash `/`
- Must be exactly: `http://localhost:8000/accounts/google/login/callback/`
- Case-sensitive
- No extra spaces

### 4. Save Changes

Click **SAVE** at the bottom of the page.

### 5. Restart Django Server

```bash
python manage.py runserver
```

### 6. Test Again

1. Go to: `http://localhost:8000/users/login/`
2. Click "Continue with Google"
3. It should work now!

## Multiple Redirect URIs

You can add multiple redirect URIs if needed:

**For Development:**
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

**For Production (when ready):**
```
https://yourdomain.com/accounts/google/login/callback/
```

## Current Configuration

- **Site Domain**: `localhost` (fixed)
- **Expected Redirect URI**: `http://localhost:8000/accounts/google/login/callback/`
- **Client ID**: Stored in `.env` file (GOOGLE_OAUTH_CLIENT_ID)

## Common Mistakes to Avoid

❌ **Wrong**: `http://localhost:8000/accounts/google/login/callback` (missing trailing slash)
❌ **Wrong**: `http://localhost/accounts/google/login/callback/` (missing port)
❌ **Wrong**: `https://localhost:8000/accounts/google/login/callback/` (using https instead of http)
✅ **Correct**: `http://localhost:8000/accounts/google/login/callback/`

## Still Not Working?

1. **Clear browser cache** - Try incognito/private mode
2. **Verify the URI is saved** - Check Google Cloud Console again
3. **Wait a few minutes** - Google changes can take a moment to propagate
4. **Check Django logs** - Look for any error messages
5. **Verify OAuth consent screen** - Make sure it's configured

## Need Help?

If you're still getting errors:
1. Check the exact error message
2. Verify the redirect URI in Google Cloud Console matches exactly
3. Make sure you're using the correct OAuth client ID
4. Ensure the OAuth consent screen is properly configured

