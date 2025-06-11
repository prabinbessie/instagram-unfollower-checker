## [4.5.0] – 2025-06-11

### Added
- **Analytics Dashboard**  
  - New detailed dashboard panel showing breakdowns for:
    - Mutual Followers  
    - Non-Followers (users you follow who don’t follow back)  
    - Not-Following-Back (users who follow you but you don’t follow)  
    - Follow-Back Ratio (%)  
  - Interactive Chart graphs for:
    - Relationship Breakdown (doughnut)  
    - Follow Comparison (bar)  
- **CSV Export**  
  - Added export buttons for multiple data types:
    - `not_following_back`  
    - `all_following`  
  - Downloads CSV files directly from the dashboard  
- **PDF Report**  
  - “Download PDF Report” button now accessible from both summary results and dashboard

### Changed
- **UI & Layout**  
  - Refactored `style.css` to leverage flex and CSS grid for fully responsive views  
  - Restyled upload cards, file-drop zones and result panels for better clarity on mobile and desktop  
  - Improved tab styling and active-state indicator for user-lists  
- **UX Improvements**  
  - Always-clear previous results on file-select or “Clear” button click  
  - Smooth scroll to dashboard on analysis completion  
  - Real-time “Preparing CSV…” progress text

### Fixed
- **Bug Fixes**  
  - Fixed drop-zone “hover” state not clearing after drag-leave  
  - Corrected broken “Not Following Back” tab content selector

### Internal / Maintenance
- Cleaned up unused CSS selectors and consolidated media-queries  
- added new ss 

---

*Enjoy seamless HTML/JSON handling, sharper visuals, and richer reports!*  
