# 🚨 URGENT: Fix Redirect URI Mismatch

## The Problem

Your browser is using `127.0.0.1` instead of `localhost`, and Google Cloud Console only has `localhost` registered.

**Error shows:** `redirect_uri=http://127.0.0.1:8000/accounts/google/login/callback/`

## ✅ Quick Fix (2 minutes)

### Add BOTH redirect URIs in Google Cloud Console:

1. **Go to**: [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. **Click** your OAuth 2.0 Client ID (check your `.env` file for the Client ID)
3. **Under "Authorized redirect URIs"**, add **BOTH** of these:

   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

4. **Click SAVE**
5. **Restart Django server**: `python manage.py runserver`
6. **Try again** - it should work now!

## Why Both?

- `localhost` and `127.0.0.1` are the same thing, but **Google treats them as different**
- Your browser might use either one depending on how you access the site
- Adding both ensures it works regardless

## Visual Guide

In Google Cloud Console, your "Authorized redirect URIs" should look like this:

```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

Both lines should be there, each on its own line.

## After Adding Both URIs

1. ✅ Save in Google Cloud Console
2. ✅ Restart Django: `python manage.py runserver`
3. ✅ Clear browser cache or use incognito mode
4. ✅ Try Google login again

## Still Not Working?

If you still get errors:
1. Wait 1-2 minutes (Google changes can take time to propagate)
2. Make sure you clicked SAVE in Google Cloud Console
3. Verify both URIs are exactly as shown above (with trailing slashes)
4. Try accessing your site via `http://localhost:8000` instead of `http://127.0.0.1:8000`

