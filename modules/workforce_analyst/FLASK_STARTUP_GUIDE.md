# 🏢 Deal Underwriting Assistant - Flask Web Application

## 🚀 Quick Start Guide

Your Streamlit app has been successfully converted to a Flask web application! This eliminates authentication issues and provides stable team access.

### 1. Install Required Dependencies

```bash
cd "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/workforce_analyst"
python3 -m pip install -r requirements.txt
```

### 2. Start the Flask Server

```bash
python3 flask_app.py
```

You'll see output like:
```
🏢 Deal Underwriting Assistant - Flask Web Server
==================================================
🚀 Starting server...
📱 Access at: http://localhost:5001
🌐 Team access: http://[your-ip]:5001
⏹️  Press Ctrl+C to stop
==================================================
```

### 3. Access the Application

- **Local access**: Open `http://localhost:5001` in your browser
- **Team access**: Others can access via `http://[your-ip-address]:5001`

## ✅ Key Improvements

### What's Fixed
- ❌ **No more Google Sheets authentication issues**
- ❌ **No more Streamlit connection problems**  
- ❌ **No team download requirements**
- ✅ **Direct Excel file operations**
- ✅ **Stable web interface**
- ✅ **Multi-user simultaneous access**

### Features Available
- 🔍 **Deal browsing** - Browse all deals in your Dropbox folder
- 🤖 **AI data extraction** - OpenAI-powered document analysis
- 📊 **BOTN generation** - Excel templates saved directly to deal folders
- 💾 **Deal caching** - Fast access to previously analyzed deals
- 🔄 **Session management** - Track progress through workflow stages

## 📁 File Structure

```
workforce_analyst/
├── flask_app.py              # Main Flask application
├── AcquisitionAnalyst.py     # Business logic (updated for Excel)
├── requirements.txt          # Dependencies (updated for Flask)
├── templates/                # HTML templates
│   ├── base.html            # Base template with styling
│   ├── index.html           # Dashboard
│   ├── deals.html           # Deal browsing
│   ├── extract.html         # Data extraction
│   ├── botn.html            # BOTN analysis
│   ├── results.html         # Results & file access
│   └── error.html           # Error handling
└── deal_cache/              # Cached deal data (JSON files)
```

## 🔧 Technical Details

### Excel Integration
- **Template Path**: `/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals/!WFBOTN/80AMIBOTN.xlsx`
- **Output Location**: Each deal folder gets its own BOTN file
- **No Authentication**: Direct file operations, no Google API required

### Business Logic
- All existing data extraction logic preserved
- Same AI processing with OpenAI API
- Same caching system for fast access
- Compatible with existing deal folder structure

### Web Interface
- Modern Bootstrap 5 styling
- Mobile-responsive design
- Real-time progress indicators
- AJAX for smooth interactions

## 🛠️ Usage Workflow

1. **Browse Deals** - Select from available deal folders
2. **Extract Data** - AI analyzes PDFs and documents  
3. **Generate BOTN** - Excel file created with extracted data
4. **Review Results** - Open file directly or view in browser
5. **Team Access** - Multiple users can work simultaneously

## 🔍 Testing & Validation

The application includes built-in testing:
- Template accessibility test
- File operation validation
- Error handling and recovery
- System status monitoring

## 📞 Support

If you encounter any issues:
1. Check template file access
2. Verify OpenAI API key
3. Ensure sufficient disk space
4. Review error logs in Flask console

---

**🎉 Congratulations!** Your deal analysis workflow is now running on a stable web platform with no authentication headaches.