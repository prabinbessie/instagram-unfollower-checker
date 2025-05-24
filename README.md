# 📉 Instagram Unfollower Checker

[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/prabinbessie/instagram-unfollower-checker/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Contributions](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

A Flask-powered web app to find Instagram accounts you follow that don’t follow you back. Supports both JSON and HTML data exports directly from Instagram.

🔗 **Live Demo**: [instagram-unfollower-checker.onrender.com](https://instagram-unfollower-checker-nm16.onrender.com)

---

## Key Features

- **Dual-format Import**  
  Accepts both Instagram’s HTML and JSON data exports (followers & following).

- **Smart File Detection**  
  Automatically swaps/fixes reversed uploads by inspecting filenames or content.

- **Instant Web Results**  
  Mobile-responsive list view of all non-reciprocal follows with clickable profile links.

- **On-demand PDF Report**  
  Generate and download a styled PDF report, with embedded links and clear layout.

- **Lightweight & Secure**  
  No external API calls, all processing happens in your server memory. Strict file-type and size checks, plus modern security headers.

- **Extensible Architecture**  
  Modular analyzer class, easy to add CSV or Excel export in future.

---

## v4.0.0 — Recent Improvements

**Added**  
- “Clear” button to reset form & results without reloading  
- Automatic version bump from `version.py` into UI badge  
- Context-aware error summaries (client + server)

**Improved**  
- Streamlined file-swap detection logic for faster analysis  
- Enhanced mobile layout and button feedback animations  
- More precise file-size and format validation messages

**Fixed**  
- Occasional loading overlay hang on slow networks  
- PDF `Content-Disposition` header omissions in Firefox/Edge  
- Edge cases in HTML parser when Instagram markup changes

---

##  Installation
```bash
### Clone repository
- `git clone https://github.com/prabinbessie/instagram-unfollower-checker.git`
- `cd instagram-unfollower-checker`

### Create virtual environment
- `python -m venv venv`

### Activate environment
- `source venv/bin/activate`  # Linux/macOS
- `.\venv\Scripts\activate`   # Windows

### Install dependencies
- `pip install -r requirements.txt`

### Start development server
`flask run --port 5000 --debug`
```
## Privacy & Data Handling

This tool **does not collect, store, or access** your Instagram data in any way.All data processing happens locally in your browser or server memory during the session.

-  No login or API access to Instagram
-  No data is sent to third-party servers
-  Files are deleted after session ends or when the tab is closed
- You are in full control of your data

---

##  How to Get Your Instagram Data (With Screenshots)

To use this tool, you’ll need to manually download your Instagram data. Here’s how:

1. **Go to Instagram → Settings → Your Information and Permisson → Download your information**
2. Select **"Following and Followers"** (or "Connections")
3. Choose **JSON** or **HTML**(SupportFromV3) as the format
4. Submit your request and wait for an email
5. Download the ZIP file from the link in the email
6. Extract it, and upload on our hosted:
   - `followers_1.json` or `followers.html`
   - `following.json` or `following.html`

![Instagram Data Download Screenshot](static/img/instagram_data_download.jpg)

---

## What Do You Get?

Once the files are uploaded, the tool processes them and shows:

-  A list of accounts you follow who don’t follow you back
-  Clickable profile links right in your browser
-  Styled PDF report for easy sharing or archiving

![Sample Output Screenshot](static/img/sample_results.png)

##  Technical Architecture

```plaintext
instagram-unfollower-checker/
├── static/
│   └── css/
├── templates/
├── sample_json/           
│   ├── followers.json
│   └── following.json
├── tests/
├── .gitignore
├── CHANGELOG.md
├── Procfile
├── README.md
├── LICENSE
├── app.py
├── requirements.txt
└── version.py
```
  

## 🤝 Contributing

### We welcome contributions! Please follow these steps:

- Fork the repository
- Clone your fork locally
- Create feature branch:
`git checkout -b feat/your-feature`
- Implement code with type hints, PEP-8 style, and tests
- Update CHANGELOG.md
- Push changes:
`git push origin feat/your-feature`
- Create Pull Request with detailed description
##  License

Distributed under [MIT License](LICENSE). See LICENSE for full text.
## Contact
---
**Prabin Bhandari**
-  em8een@gmail.com
-  Instagram @prabinbhandarii
---