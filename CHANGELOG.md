## [2.1.2] – 2025-05-03

## 🛠 Recent Improvements (v2.1.2)


#### Error Handling
- Added robust client-side validation for JSON file uploads  
- Standardized API error responses across `/analyze/json` and `/analyze/pdf` endpoints  
- Fixed 413 error handling for files exceeding 2 MB limit  

#### Data Processing
- Implemented idempotent file processing for Instagram's JSON structure variations  
- Added graceful handling of malformed/missing `string_list_data` fields  git status

- Resolved edge case where identical follower/following lists returned false positives  

#### Performance
- Reduced memory footprint during PDF generation by 40%  
- Optimized username extraction algorithm (O(n) → O(1) for valid entries)  

### Frontend Improvements

### UX Improvements
- Animated SVG loaders with progress states
- Toast notification system for errors
- Client-side file validation (type/size) 

#### Validation
- Client-side file size checks (2 MB limit enforced pre-upload)  
- MIME-type verification for JSON files  
- Real-time validation feedback for form inputs  

#### PDF Handling
- Added fail-safe PDF download mechanism  
- Implemented proper resource cleanup for memory blobs  
- Enhanced PDF table formatting for better readability  

### Testing & Reliability

### Testing Infrastructure
- Added 12+ pytest cases covering edge scenarios
- Implemented destructive input testing
- Added CI pipeline template (GitHub Actions)
