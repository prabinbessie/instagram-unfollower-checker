**Version**: v2.1.2
# 📉 Instagram Unfollower Detective

[![Version](https://img.shields.io/badge/version-2.1.2-blue.svg)](https://github.com/prabinbessie/instagram-unfollower-checker/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Contributions](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

A Flask-powered tool to analyze Instagram relationships and identify non-reciprocal follows. Supports both JSON and PDF exports from Instagram.

🔗 **Live Demo**: [instagram-unfollower-checker.onrender.com](https://instagram-unfollower-checker.onrender.com)

---

## 🚀 Key Features

### Dual Format Support
- ✅ Handles both legacy and modern Instagram JSON formats
- 📦 Processes nested (`relationships_followers`) and flat structures
- 🧩 Automatic format detection with fallback mechanisms

### Performance & Security
- 🚀 O(1) lookup performance for datasets >100k entries
- 🛡️ Content validation (MIME types, size limits <2MB)
- 📈 40% memory reduction in PDF generation

### Multi-Format Reporting
- 📄 PDF with clickable profile links
- 📱 Mobile-optimized HTML results
- 📋 CSV export (beta - v2.2 preview)

---

## 🛠 Recent Improvements (v2.1.2)

### Core Enhancements
- Added Instagram's 2024 JSON format support
- Implemented hybrid format detection algorithm
- Reduced PDF memory footprint by 40%
- 📁 Added sample JSON files for testing and demo purposes (`sample_json/`)


### Testing Infrastructure
- Added 12+ edge case test scenarios
- Implemented destructive input testing
- GitHub Actions CI pipeline template

### User Experience
- 🎨 Animated SVG loaders with progress states
- 📢 Toast notification system for errors
- 📁 Client-side file validation (type/size)

---

## 📦 Installation

### Clone repository
- `git clone https://github.com/prabinbessie/instagram-unfollower-checker.git`
- `cd instagram-unfollower-checker`

### Create virtual environment
- `python -m venv venv`

### Activate environment
- `source venv/bin/activate`  # Linux/macOS
- `.\venv\Scripts\activate`   # Windows

### Install dependencies
`pip install -r requirements.txt`

### Start development server
`flask run --port 5000 --debug`

## 🔒 Privacy & Data Handling

This tool **does not collect, store, or access** your Instagram data in any way.All data processing happens locally in your browser or server memory during the session.

- ❌ No login or API access to Instagram
- ❌ No data is sent to third-party servers
- ✅ Files are deleted after session ends or when the tab is closed
- ✅ You are in full control of your data

---

## 📥 How to Get Your Instagram Data (With Screenshots)

To use this tool, you’ll need to manually download your Instagram data. Here’s how:

1. **Go to Instagram → Settings → Your Information and Permisson → Download your information**
2. Select **"Following and Followers"** (or "Connections")
3. Choose **JSON** as the format
4. Submit your request and wait for an email
5. Download the ZIP file from the link in the email
6. Extract it, and upload :
   - `followers.json`
   - `following.json`

![Instagram Data Download Screenshot](static/img/instagram_data_download.png)

---

## 🧾 What Do You Get?

Once the files are uploaded, the tool processes them and shows:

- 🔗 Clickable Instagram profile links
- ❌ People you follow who don’t follow you back
- 📄 Downloadable PDF report
- 📊 Visual summary (CSV export coming soon)

![Sample Output Screenshot](static/img/sample_results.png)

### Immediate PDF download
- CSV export (In V3 )
- Shareable link (24h retention (in V3))
## 🧩 Technical Architecture

├── instagram-unfollower-checker/
│   ├── static/
│   │   └── css/
│   ├── templates/
│   ├── sample_json/           
│   │   ├── followers.json
│   │   └── following.json
│   ├── .gitignore
│   ├── CHANGELOG.md
│   ├── Procfile
│   ├── README.md
│   ├── app.py
│   ├── requirements.txt
│   └── version.py
  

## 🤝 Contributing

### We welcome contributions! Please follow these steps:

- Fork the repository
- Clone your fork locally
- Create feature branch:
`git checkout -b feat/your-feature`
-Implement changes with:
-Type hints for new code
-PEP-8 compliance
- 90%+ test coverage
- Update CHANGELOG.md
- Push changes:
`git push origin feat/your-feature`
- Create Pull Request with detailed description
##  📜 License

Distributed under MIT License. See LICENSE for full text.

##  📬 Contact

**Prabin Bhandari**
- 📧 bhandariprabin84@gmail.com
- 📱 Instagram @prabinbhandariii
- 🐦 Twitter @prabinbessie
