# Google OAuth Error Fix

## Error: "Missing required parameter: client_id"

This error usually occurs when the redirect URI in Google Cloud Console doesn't match what django-allauth is sending.

## Quick Fix Steps

### 1. Verify Redirect URI in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, make sure you have EXACTLY:

   ```
   http://localhost:8000/accounts/google/login/callback/
   ```

   **Important Notes:**
   - Must include the trailing slash `/`
   - Must match exactly (case-sensitive)
   - For production, also add: `https://yourdomain.com/accounts/google/login/callback/`

### 2. Verify OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Make sure:
   - App is in "Testing" or "Production" mode
   - Your email is added as a test user (if in Testing mode)
   - Required scopes are configured

### 3. Verify Client ID and Secret

Your current configuration is stored in:
- `.env` file
- Database (SocialApp model)

### 4. Restart Django Server

After making changes in Google Cloud Console:
```bash
python manage.py runserver
```

### 5. Clear Browser Cache

Sometimes cached OAuth responses cause issues. Try:
- Incognito/Private browsing mode
- Clear browser cache and cookies

## Common Issues

### Issue: Redirect URI Mismatch
**Solution**: The redirect URI in Google Console must match EXACTLY:
- `http://localhost:8000/accounts/google/login/callback/` (development)
- `https://yourdomain.com/accounts/google/login/callback/` (production)

### Issue: OAuth Consent Screen Not Configured
**Solution**: 
1. Go to OAuth consent screen
2. Fill in required fields (App name, User support email, etc.)
3. Add test users if in Testing mode
4. Save and continue

### Issue: Client ID Not Found
**Solution**: 
- Verify the Client ID in `.env` matches Google Cloud Console
- Check that the OAuth client is enabled
- Ensure you're using the correct project in Google Cloud Console

## Testing

1. Visit: `http://localhost:8000/users/login/`
2. Click "Continue with Google"
3. You should be redirected to Google's login page
4. After login, you'll be redirected back to the site

## Database Configuration

The SocialApp is configured in the database. To view/update:

```bash
python manage.py shell
```

```python
from allauth.socialaccount.models import SocialApp
app = SocialApp.objects.get(provider='google')
print(f"Client ID: {app.client_id}")
print(f"Sites: {[s.domain for s in app.sites.all()]}")
```

## Need Help?

If issues persist:
1. Check Django logs for detailed error messages
2. Verify all redirect URIs in Google Cloud Console
3. Ensure OAuth consent screen is properly configured
4. Try creating a new OAuth client ID if needed

