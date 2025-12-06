# GitHub Secrets Setup Instructions

This guide will help you configure GitHub secrets for CI/CD automation.

## Required Secrets

### 1. Docker Hub (Required for Docker image publishing)

**Why needed**: To push Docker images to Docker Hub registry

**Steps**:
1. Create Docker Hub account at https://hub.docker.com
2. Go to your GitHub repository
3. Navigate to: **Settings** → **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add these secrets:

| Secret Name | Description | How to get it |
|------------|-------------|---------------|
| `DOCKER_USERNAME` | Docker Hub username | Your Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password/token | Account Settings → Security → Access Tokens |

---

### 2. Heroku (Optional - for automated deployment)

**Why needed**: To deploy backend to Heroku cloud

**Steps**:
1. Create Heroku account at https://heroku.com
2. Install Heroku CLI: `curl https://cli-assets.heroku.com/install.sh | sh`
3. Login: `heroku login`
4. Create app: `heroku create your-wellbeing-app`
5. Get API key: Go to Account Settings → API Key
6. Add GitHub secrets:

| Secret Name | Description | How to get it |
|------------|-------------|---------------|
| `HEROKU_API_KEY` | Heroku API key | Account Settings → API Key → Reveal |
| `HEROKU_APP_NAME` | Heroku app name | e.g., `your-wellbeing-app` |
| `HEROKU_EMAIL` | Heroku account email | Your Heroku login email |

---

### 3. Expo Token (Optional - for mobile app builds)

**Why needed**: To build Android/iOS apps with EAS

**Steps**:
1. Create Expo account at https://expo.dev
2. Install EAS CLI: `npm install -g eas-cli`
3. Login: `eas login`
4. Generate token: `eas token:create`
5. Add GitHub secret:

| Secret Name | Description | How to get it |
|------------|-------------|---------------|
| `EXPO_TOKEN` | Expo access token | Run `eas token:create` |

---

## Quick Setup Commands

### Docker Hub Setup
```bash
# 1. Create Docker Hub account
# 2. Generate access token
# 3. Add to GitHub secrets:
#    DOCKER_USERNAME = your_username
#    DOCKER_PASSWORD = dckr_pat_xxxxx
```

### Heroku Setup
```bash
# Login to Heroku
heroku login

# Create app
heroku create wellbeing-backend-prod

# Get API key
heroku auth:token

# Add to GitHub secrets:
#   HEROKU_API_KEY = your_api_key
#   HEROKU_APP_NAME = wellbeing-backend-prod
#   HEROKU_EMAIL = your@email.com
```

### Expo Setup
```bash
# Install EAS CLI
npm install -g eas-cli

# Login
eas login

# Create token
eas token:create

# Add to GitHub secrets:
#   EXPO_TOKEN = token_xxxxx
```

---

## Verifying Secrets

After adding secrets:

1. Go to GitHub repository → **Settings** → **Secrets**
2. You should see all configured secrets
3. Trigger a workflow by pushing code
4. Check **Actions** tab to see workflow run

---

## Security Best Practices

✅ **DO**:
- Use access tokens instead of passwords
- Rotate tokens regularly (every 90 days)
- Use repository secrets (not environment secrets for testing)
- Review secret access logs

❌ **DON'T**:
- Commit secrets to code
- Share secrets in issues/PRs
- Use personal tokens for production
- Store secrets in plain text

---

## Testing Without Secrets

If you don't want to set up all secrets immediately:

1. **Without Docker Hub**: Workflow will skip Docker image push
2. **Without Heroku**: Workflow will skip deployment
3. **Without Expo**: Workflow will skip mobile builds

All tests will still run! Only deployment steps are skipped.

---

## Troubleshooting

### "Secret not found" error
- Verify secret name matches exactly (case-sensitive)
- Check you added it to the correct repository
- Ensure you clicked "Add secret" to save

### Docker push fails
- Verify Docker Hub credentials are correct
- Check if token has push permissions
- Ensure repository name is correct

### Heroku deployment fails
- Verify API key is still valid
- Check app name matches Heroku app
- Ensure email matches Heroku account

---

## Optional: Local Testing

Test deployment locally before setting up CI/CD:

```bash
# Test Docker build
docker build -t test-image backend-api/

# Test Heroku deployment
cd backend-api
heroku login
git push heroku main

# Test Expo build
cd mobile-app
eas build --platform android --profile preview
```

---

**Next Steps**: Once secrets are configured, push code to trigger workflows!
