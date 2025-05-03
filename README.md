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

# Clone repository
- `git clone https://github.com/prabinbessie/instagram-unfollower-checker.git`
- `cd instagram-unfollower-checker`

# Create virtual environment
- `python -m venv venv`

# Activate environment
- `source venv/bin/activate`  # Linux/macOS
- `.\venv\Scripts\activate`   # Windows

# Install dependencies
`pip install -r requirements.txt`

# Start development server
`flask run --port 5000 --debug`

## 📚 Usage Guide

- Step 1: Export Instagram Data
- Go to Instagram Settings → Privacy & Security
- Select Download Data
- Choose Followers and Following format
- Wait for email with data download link
- Step 2: Upload Files

### Required files:
- followers.json
- following.json
- Step 3: Analyze Relationships

### Results include:
- 🔗 Instagram profile links
- 📊 Activity indicators
- 🚫 Non-reciprocal follows
- Export Options

### Immediate PDF download
- CSV export (In V3 )
- Shareable link (24h retention (in V3))
## 🧩 Technical Architecture

-instagram-unfollower-checker/
├── app/                  # Core application logic
│   ├── processors/       # Data transformation handlers
│   └── utils/            # Helper functions
├── tests/                # Test suite (pytest)
│   ├── unit/             # Component tests
│   └── integration/      # End-to-end workflows
├── templates/            # Jinja2 templates
├── static/               # Web assets
│   ├── css/              # Style sheets
│   └── js/               # Client-side logic
└── requirements.txt      # Dependency manifest

## 🤝 Contributing

## We welcome contributions! Please follow these steps:

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
## 📜 License

Distributed under MIT License. See LICENSE for full text.

## 📬 Contact

- Prabin Bhandari
- 📧 bhandariprabin84@gmail.com
- 📱 Instagram @prabinbhandariii
- 🐦 Twitter @prabinbessie
