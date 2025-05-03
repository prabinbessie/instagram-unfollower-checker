**Version**: v2.1.2
# 📉 Instagram Unfollower Detective

[![Version](https://img.shields.io/badge/version-2.1.2-blue.svg)](https://github.com/prabinbessie/instagram-unfollower-checker/releases)
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
## 🛠 Recent Improvements (v2.1.2)

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

## 📚 Usage Guide

### Export Instagram Data
- Navigate to Settings → Security → Download Data → Select "Followers and Following."
- Upload Files
- Upload both followers.json and following.json files (required).
Analyze Relationships
The results will show users who don't follow you back, along with:
Instagram profile links
Follow timestamps
Account activity indicators

### Export Options
You can download the report in the following formats:
📄 PDF Report (immediate download)
📋 CSV Export (beta)
🔗 Shareable Link (24h retention)

## 🧩 Technical Architecture
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
## 🤝 How to Contribute
If you would like to contribute to the project, follow the steps below:
- Fork the repository
- Create a personal copy of the repository on GitHub.
Create a new branch
### For example:
- git checkout -b feat/awesome-feature
- Make your changes
- Ensure that your changes follow the project's coding standards and 
- include tests where necessary.
Commit your changes
Use a meaningful commit message, such as:
git commit -m "feat: add awesome feature"
Push to your fork
Push your branch to your forked repository on GitHub:
git push origin feat/awesome-feature
Open a Pull Request
Open a pull request to the original repository. Provide a description of the changes and why they are useful.
### Development Requirements:
- 90%+ test coverage
- PEP-8 compliance
- Type hints for new code
Update CHANGELOG.md with new features and fixes

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for more details.

## 📬 Contact
For any support or issues:
📧 Email: bhandariprabin84@gmail.com
😎Instagram: @prabinbessiehere