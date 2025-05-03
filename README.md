**Version**: v2.1.1
# 📉 Instagram Unfollower Checker

[![Version](https://img.shields.io/badge/version-2.1.1-blue.svg)](https://github.com/prabinbessie/instagram-unfollower-checker/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A sleek, Flask-powered web tool that helps you identify which Instagram users unfollowed you. Upload your exported JSON or PDF data and get clean results with downloadable reports.

🔗 **Live Demo**: [instagram-unfollower-checker.onrender.com](https://instagram-unfollower-checker.onrender.com)

---

## 🔍 Features

- ✅ **Smart Upload Support**
  - Accepts both Instagram **JSON** exports and **PDF** input
  - Client-side checks: file size (max 2MB), file type validation

- 🚀 **Fast & Fault-Tolerant**
  - Graceful fallback for malformed or missing `string_list_data`
  - Optimized processing from O(n) to O(1) for valid entries
  - Handles identical follower/following lists correctly

- 🛠 **Robust Error Handling**
  - Consistent API error messages
  - Clear handling of `413 Payload Too Large` errors
  - Toast notifications and animated loaders for user feedback

- 📄 **Styled PDF Export**
  - Clean PDF report with table formatting and profile links
  - Reduced memory usage by 40% for large exports

- 🧪 **Test Suite**
  - 12+ test cases using `pytest` for edge cases and malformed data
  - `--version` CLI support
  - Includes destructive input testing

---

## 📂 File Structure

instagram-unfollower-checker/
├── static/
│ └── css/
│ └── styles.css # App-wide CSS
├── templates/
│ ├── index.html # Upload form & homepage
│ └── results.html # Display & PDF link
├── Test/
│ └── test_app.py # pytest test cases
├── .gitignore
├── CHANGELOG.md # Version history
├── Procfile # For Render/Heroku deployment
├── README.md # This file
├── app.py # Flask app & route handling
├── requirements.txt # Python dependencies
└── version.py # App version constant

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip
- Optional: virtualenv or venv

### Installation

```bash
# Clone the repo
git clone https://github.com/prabinbessie/instagram-unfollower-checker.git
cd instagram-unfollower-checker

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
flask run
Or use the Heroku/Render Procfile locally:
heroku local
Visit: http://localhost:5000
🏗 Usage

Open the app in your browser.
Choose whether to upload a JSON or PDF file.
Drag & drop your Instagram data export.
View results in a scrollable interface with links.
Download a styled PDF report of unfollowers.
📜 Changelog

See CHANGELOG.md for full details.
v2.1.1 Highlights:
🎯 JSON edge case handling (missing fields, false positives)
📉 Memory optimization in PDF generation
✅ 12+ test cases & destructive testing
📦 Client-side file validation (size + MIME type)
🖼 Scrollable UI + animated loaders + toast notifications
💬 Contributing

Want to contribute?
Fork this repo
Create your feature branch: git checkout -b feature/awesome-feature
Commit your changes: git commit -m 'feat: add awesome feature'
Push to the branch: git push origin feature/awesome-feature
Open a Pull Request
🧪 Please include test coverage and follow clean coding practices.
📄 License

This project is licensed under the MIT License.
See LICENSE for more info.
Built with ❤️ by @prabinbessie

---

Let me know if you also want:
- A screenshot section
- Badges for deployments/tests
- A `CONTRIBUTING.md` or `CODE_OF_CONDUCT.md` template  
Would you like those now?