## [3.0.0] – 2024-03-20

### Added
- **HTML + JSON Support**  
  - Automatic detection of Instagram export format (`.html` vs. `.json`) in `InstagramAnalyzer.detect_file_type()`  
  - New `parse_html()` method leveraging BeautifulSoup to extract usernames from HTML export files  
- **PDF Report Enhancements**  
  - Hyperlinked “Profile Link” column in generated PDF, pointing directly to `https://www.instagram.com/{username}`  
- **UI & UX Improvements**  
  - Instagram-inspired gradient header and dashed drop-zone file-upload box  
  - Interactive username links with hover animation for web results  

### Changed
- **Core Refactoring**  
  - Consolidated extraction logic in `InstagramAnalyzer`: `extract_users()`, `_extract_json_users()`, and new file-type dispatch  
  - New `validate_files()` method with explicit checks for required uploads, empty files, and permitted extensions  
- **Dependency Bumps**  
  - Flask → **3.0.2**  
  - beautifulsoup4 → **4.12.3**  
  - reportlab → **4.1.0**  
  - python-dotenv → **1.0.0**  
- **Backward Compatibility**  
  - Legacy JSON workflows remain unchanged—existing users upgrading to v3 see zero disruption  
  Changelog Summary
Form Handling
Added form reset post-submission
Removed auto PDF download; added manual trigger
Improved error handling and user feedback
File Validation
Client- and server-side file type/size validation
Enhanced JSON structure detection and error messages
PDF Generation
Moved to a separate endpoint
Triggered via button; independent of initial analysis
Preserves form state for consistent output
UI Enhancements
Custom file upload buttons and better visual hierarchy
Collapsible data guide and improved footer styling
Clearer feedback and form reset behavior
Security
Strict file type checks and size enforcement
Session-free architecture
Extended error logging and multi-level validation
Testing Coverage
Validates file types and sizes
Ensures proper handling of mutual follows and swaps
Verifies stable PDF generation and UI reset

### Documentation
- **README.md**  
  - Added “How to Get HTML Files” section with step-by-step instructions for downloading and locating Instagram’s HTML exports  
  - Detailed “Version 3 Features” overview  
- **CHANGELOG.md**  
  - Introduced this v3 entry  
- **LICENSE**  
  - Added standard MIT License file

---

*Enjoy seamless HTML/JSON handling, sharper visuals, and richer reports!*  
