**Version**: v2.1.2
# 📉 Instagram Unfollower Detective

[![Version](https://img.shields.io/badge/version-2.1.1-blue.svg)](https://github.com/prabinbessie/instagram-unfollower-checker/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

A Flask-powered tool to analyze Instagram relationships and identify non-reciprocal follows. Supports both JSON and PDF exports from Instagram.

🔗 **Live Demo**: [instagram-unfollower-checker.onrender.com](https://instagram-unfollower-checker.onrender.com)

---

## 🚀 Key Features

- **Dual Format Support**
  - ✅ Handles Instagram's legacy and modern JSON formats
  - 📦 Processes nested (`relationships_followers`) and flat structures
  - 🧩 Automatic format detection for seamless compatibility

- **Smart Analysis**
  - 🚀 O(1) lookup performance for large datasets
  - 🛡️ Graceful error recovery for malformed data
  - 📈 Memory-optimized processing (40% reduction)

- **Multi-Output Reports**
  - 📄 PDF export with clickable profile links
  - 📱 Mobile-optimized HTML results
  - 📋 CSV export (coming in v2.2)

- **Enterprise-Grade Security**
  - 🔒 2MB file size limit with MIME validation
  - 🛡️ Strict content security policies
  - ⚠️ Comprehensive error logging

---

## 🛠 Recent Improvements (v2.1.1)

### Core Enhancements
- Added dual-format JSON parsing for Instagram's API changes
- Implemented format auto-detection algorithm
- Reduced memory footprint by 40% in PDF generation

### Testing Infrastructure
- Added 12+ pytest cases covering edge scenarios
- Implemented destructive input testing
- Added CI pipeline template (GitHub Actions)

### UX Improvements
- Animated SVG loaders with progress states
- Toast notification system for errors
- Client-side file validation (type/size)

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/prabinbessie/instagram-unfollower-checker.git
cd instagram-unfollower-checker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
flask run --port 5000 --debug

📚 Usage Guide

Export Instagram Data
Settings → Security → Download Data → Select "Followers and Following"
Upload Files
followers.json (required)
following.json (required)
Analyze Relationships
Results show users who don't follow you back with:
Instagram profile links
Follow timestamps
Account activity indicators
Export Options
PDF Report (immediate download)
CSV Export (beta)
Shareable Link (24h retention)

🧩 Technical Architecture

text
instagram-unfollower-checker/
├── app/                  
│   ├── processors/       
│   └── utils/            
├── tests/                
│   ├── unit/             
│   └── integration/      
├── templates/            
├── static/               
│   ├── css/              
│   └── js/               
└── requirements.txt  

🤝 Contributing

Fork the repository
Create feature branch:
git checkout -b feat/your-feature
Commit changes:
git commit -m "feat: add awesome feature"
Push to branch:
git push origin feat/your-feature
Open a Pull Request
Development Requirements:

90%+ test coverage
PEP-8 compliance
Type hints for new code
Update CHANGELOG.md
📜 License

MIT License - See LICENSE for full text.

📬 Contact

For support/issues:
📧 bhandariprabin84@gmail.com
🐦 @prabinbessie