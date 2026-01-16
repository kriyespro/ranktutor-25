# Google OAuth Setup Guide

This guide explains how to set up Google OAuth login for RankTutor platform.

## Prerequisites

1. Django-allauth is already installed and configured
2. Google OAuth credentials are required

## Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - For development: `http://localhost:8000/accounts/google/login/callback/`
     - For production: `https://yourdomain.com/accounts/google/login/callback/`
   - Save and copy the Client ID and Client Secret

## Step 2: Configure Environment Variables

Add the following to your `.env` file (or environment variables):

```env
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here
```

## Step 3: Run Migrations

After installing django-allauth, run migrations to create necessary database tables:

```bash
python manage.py migrate
```

## Step 4: Create Site Entry

Django-allauth requires a Site entry. Create it via Django admin or shell:

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'localhost:8000'  # or your production domain
site.name = 'RankTutor'
site.save()
```

## Step 5: Test Google Login

1. Start the development server
2. Navigate to `/users/login/` or `/users/register/`
3. Click "Continue with Google" or "Sign up with Google"
4. Complete the Google OAuth flow
5. For new users, you'll be prompted to select your role (Student, Parent, Tutor, etc.)
6. After signup, you'll be redirected to the appropriate dashboard based on your role

## Features

- **All User Types Supported**: Google login works for all user roles:
  - Students
  - Parents
  - Tutors
  - City Admins
  - Global Admins

- **Role Selection**: New users signing up via Google will be prompted to select their role

- **Email Verification**: Google-authenticated users have their email automatically verified

- **Seamless Integration**: Google login buttons are available on both login and registration pages

## Troubleshooting

### Issue: "Redirect URI mismatch"
- Solution: Ensure the redirect URI in Google Console matches exactly: `/accounts/google/login/callback/`

### Issue: "Invalid client ID"
- Solution: Verify `GOOGLE_OAUTH_CLIENT_ID` in your `.env` file

### Issue: "Social account signup form not showing role"
- Solution: Ensure `SOCIALACCOUNT_AUTO_SIGNUP = False` in settings.py (already configured)

### Issue: Users not being redirected correctly
- Solution: Check the `CustomAccountAdapter` and `CustomSocialAccountAdapter` in `users/adapters.py`

## Notes

- The default role for Google signups is 'student' if not specified
- Users can change their role later in their profile settings (if allowed)
- Email addresses from Google are automatically marked as verified
- User profiles are automatically created for Google-authenticated users

