# Acquisition Analyst Setup Guide

## Prerequisites

1. **OpenAI API Key**: Get yours from https://platform.openai.com/api-keys
2. **Google OAuth2 Client**: For accessing Google Sheets and Drive

## Setting up Google OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Google Sheets API
   - Google Drive API
4. Create OAuth2 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "CREATE CREDENTIALS" > "OAuth client ID"
   - Choose "Desktop application" as the application type
   - Name it (e.g., "Acquisition Analyst")
   - Click "CREATE"
   - Download the JSON configuration file
5. Copy the JSON content from the downloaded file

## Running the Application

1. Use the provided script:
   ```bash
   ./run.sh
   ```

2. Or run directly:
   ```bash
   /Users/vitorfaroni/Documents/Automation/venv/bin/streamlit run AcquisitionAnalyst.py
   ```

## First Time Setup

1. When the app opens, expand the "🔑 API Keys" section in the sidebar
2. Enter your OpenAI API key
3. Paste your Google OAuth2 Client Config JSON in the text area
4. Click "Authenticate with Google"
5. Follow the OAuth flow:
   - Click the Google authentication link
   - Sign in to your Google account
   - Grant permissions to access Sheets and Drive
   - Copy the authorization code and paste it back in the app
6. The template ID is already pre-filled

## OAuth2 vs Service Account

OAuth2 is more secure and user-friendly because:
- No need for JSON key files
- Uses your personal Google account
- More granular permissions
- Works around organizational restrictions
- Easier to revoke access

## Important Notes

- The app looks for deals in: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals`
- Each deal folder should contain either an OM or Executive Summary PDF
- If no OM is found, you can manually enter the data
- The app creates a copy of your template for each deal analyzed
- Authentication tokens are saved locally for convenience