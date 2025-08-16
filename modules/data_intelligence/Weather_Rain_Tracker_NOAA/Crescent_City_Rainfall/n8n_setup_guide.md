# KCEC Weather Data Collection with n8n

This guide shows how to set up automated daily weather data collection for KCEC using n8n.

## Option 1: Import Ready-Made Workflow

1. **Import the workflow**:
   - Open n8n
   - Go to Workflows → Import
   - Upload `n8n_kcec_weather_workflow.json`

2. **Set up credentials**:
   - **NOAA API**: 
     - Click on "Get NOAA Data" node
     - Add credentials → HTTP Header Auth
     - Header Name: `token`
     - Header Value: `oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA`
   
   - **Google Sheets** (optional):
     - Connect your Google account
     - Create a sheet with columns: Date, Precipitation_Inches, Temperature_F, Humidity_Percent, Timestamp

3. **Activate the workflow**:
   - Toggle the workflow to "Active"
   - It will run daily at 9 AM

## Option 2: Use Python Script with Execute Command Node

1. **Create a new workflow** with these nodes:
   - Schedule Trigger (daily)
   - Execute Command node
   - Set node (to parse JSON)
   - Your choice of output (Database, Sheets, Email, etc.)

2. **Configure Execute Command node**:
   ```bash
   python3 /path/to/kcec_n8n_simple.py 1
   ```
   - The `1` means get 1 day of data (yesterday)
   - Returns JSON with precipitation data

3. **Parse the JSON output**:
   - Use a Set node to extract the fields you need
   - Example expressions:
     - `{{ JSON.parse($json.stdout).yesterday.precipitation_inches }}`
     - `{{ JSON.parse($json.stdout).current_conditions.temperature_f }}`

## Option 3: HTTP Webhook Integration

1. **Run the webhook server**:
   ```bash
   python3 kcec_n8n_webhook.py
   ```

2. **In n8n, use HTTP Request node**:
   - URL: `http://localhost:5000/webhook/weather/daily`
   - Method: GET
   - Returns yesterday's weather + current conditions

## Data Structure

The scripts return data in this format:

```json
{
  "execution_time": "2024-01-15T09:00:00Z",
  "station": "KCEC - Crescent City, Jack McNamara Field Airport",
  "yesterday": {
    "date": "2024-01-14",
    "precipitation_inches": 0.25,
    "has_data": true
  },
  "current_conditions": {
    "temperature_f": 55.4,
    "humidity_percent": 78,
    "precipitation_last_hour_inches": 0.05
  },
  "summary": {
    "total_precipitation_inches": 0.25,
    "days_with_precipitation": 1
  }
}
```

## Example n8n Use Cases

### 1. Daily Email Report
- Schedule Trigger → Execute Command → Email node
- Send daily precipitation summary

### 2. High Precipitation Alert
- Add IF node after data collection
- Condition: `{{ $json.yesterday.precipitation_inches > 0.5 }}`
- Send alert via Slack/Email/SMS

### 3. Weekly Summary
- Change script parameter to `7` for weekly data
- Create formatted report
- Send to stakeholders

### 4. Database Storage
- PostgreSQL/MySQL node after data collection
- Build historical database
- Create dashboards with Metabase/Grafana

### 5. Integration with AI Agent
- Send data to OpenAI/Anthropic node
- Generate weather insights
- Create natural language reports

## Advantages of n8n Integration

1. **No server needed** - n8n handles scheduling
2. **Visual workflow** - Easy to modify and extend
3. **Error handling** - Built-in retry and notification
4. **Multiple outputs** - Send to multiple destinations
5. **Easy monitoring** - See execution history
6. **No code changes** - Configure via UI

## Troubleshooting

- **No data returned**: Check if NOAA has data for the requested date (usually 1-2 day delay)
- **API errors**: Verify NOAA token is valid
- **Time zone issues**: n8n uses UTC by default, adjust schedule accordingly

## Advanced: Custom Code Node

Instead of external Python script, use n8n Code node:

```javascript
const axios = require('axios');

// NOAA API call
const noaaResponse = await axios.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/data', {
  headers: { 'token': 'oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA' },
  params: {
    datasetid: 'GHCND',
    stationid: 'GHCND:USW00093814',
    datatypeid: 'PRCP',
    startdate: new Date(Date.now() - 86400000).toISOString().split('T')[0],
    enddate: new Date().toISOString().split('T')[0],
    limit: 1000,
    units: 'standard'
  }
});

// Process and return data
return {
  precipitation_inches: noaaResponse.data.results[0]?.value / 10 / 25.4 || 0,
  date: new Date(Date.now() - 86400000).toISOString().split('T')[0]
};
```

This keeps everything within n8n!