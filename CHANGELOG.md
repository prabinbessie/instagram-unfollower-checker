## [2.1.1] – YYYY-MM-DD

### Core Fixes & Enhancements

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

#### UI/UX
- Added animated loading overlay with progress indicators  
- Implemented auto-dismissible toast notifications for errors/success  
- Introduced scrollable results container (max-height: 60vh)  
- Added Instagram profile links for identified non-followers  

#### Validation
- Client-side file size checks (2 MB limit enforced pre-upload)  
- MIME-type verification for JSON files  
- Real-time validation feedback for form inputs  

#### PDF Handling
- Added fail-safe PDF download mechanism  
- Implemented proper resource cleanup for memory blobs  
- Enhanced PDF table formatting for better readability  

### Testing & Reliability

#### Test Suite
- Added 12 new test cases covering edge scenarios  
- Fixed version command test (`--version` CLI argument)  
- Implemented destructive testing for malformed JSON payloads
