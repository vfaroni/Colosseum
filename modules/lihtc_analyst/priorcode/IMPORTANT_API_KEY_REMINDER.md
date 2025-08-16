# IMPORTANT: Google Maps API Key Security Reminder

## TEMPORARY API KEY IN USE
**Current Key:** AIzaSyBlOVHaaTw9nbgBlIuF90xlXHbgfzvUWAM

## ⚠️ ACTION REQUIRED ⚠️
This is a TEMPORARY Google Maps API key that MUST be changed before production use.

### Security Best Practices:
1. **Create a new API key** specifically for this project
2. **Restrict the key** to only the Places API
3. **Add application restrictions** (IP addresses or referrers)
4. **Set quota limits** to prevent unexpected charges
5. **Never commit API keys** to version control

### How to Change the API Key:

1. **Create a new key:**
   - Go to https://console.cloud.google.com/
   - Select your project
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"

2. **Update the key in these files:**
   - `/code/CLAUDE.md` - Update the API Requirements section
   - `/code/test_proximity_analyzer.py` - Update the API_KEY variable
   - `/code/texas_land_analyzer_with_proximity.py` - Update the API_KEY variable

3. **Or use environment variables (recommended):**
   ```bash
   export GOOGLE_MAPS_API_KEY='your_new_secure_key'
   ```

4. **Delete this temporary key:**
   - Go to Google Cloud Console
   - Find the temporary key (AIzaSyBlOVHaaTw9nbgBlIuF90xlXHbgfzvUWAM)
   - Click the trash icon to delete it

### Files Currently Using the API Key:
- `test_proximity_analyzer.py`
- `texas_land_analyzer_with_proximity.py`
- `CLAUDE.md` (documentation)

### Estimated API Usage:
- Each property analysis makes ~16-24 API calls (2-3 per amenity type)
- With 227 properties: ~3,632-5,448 API calls
- Google Maps gives $200 free credit monthly (~40,000 Places API calls)

**Remember:** This temporary key is exposed in your code. Change it before sharing or deploying!