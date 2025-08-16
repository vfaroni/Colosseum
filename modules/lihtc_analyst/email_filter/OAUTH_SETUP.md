# OAuth2 Setup Instructions

## 1. Install Dependencies

```bash
cd "/Users/vitorfaroni/Documents/Automation/Email Deal Filter"
pip install -r requirements.txt
```

## 2. Create Google Cloud Project and Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

## 3. Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop application"
4. Name it "Email Deal Filter"
5. Download the credentials file as `credentials.json`
6. Place it in: `/Users/vitorfaroni/Documents/Automation/Email Deal Filter/credentials.json`

## 4. Run the Script

```bash
python3 email_deal_filter_oauth.py
```

## 5. First Run Authorization

- A browser window will open
- Sign in with your vitor@synergycdc.org account
- Grant permissions to the application
- The script will save a token for future runs

## 6. Files Created

- `credentials.json` - Your OAuth2 client credentials (keep private)
- `token.pickle` - Saved authentication token (auto-generated)
- `filter_log.txt` - Activity log

## Security Notes

- Keep `credentials.json` private
- The token file allows script to access your email without re-authentication
- Revoke access anytime in your Google Account settings

## Troubleshooting

If you get authentication errors:
1. Delete `token.pickle` to force re-authentication
2. Check that Gmail API is enabled in your Google Cloud project
3. Verify `credentials.json` is in the correct location