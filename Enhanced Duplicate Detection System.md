# Enhanced Duplicate Detection System

## Overview
The news app has been significantly improved to prevent posting duplicate content on WordPress. The new system implements multiple layers of duplicate detection using various algorithms and data sources.

## Key Improvements

### 1. Multi-Layer Duplicate Detection

#### **Layer 1: URL Tracking**
- **New Feature**: Tracks processed URLs to prevent reprocessing the same article
- **Implementation**: Uses MD5 hash of URLs stored in JSON file (`posted_articles_urls.json`)
- **Benefit**: Prevents same article from different aggregators being processed twice

#### **Layer 2: Enhanced Title Similarity**
- **Improvement**: Uses multiple fuzzy matching algorithms instead of just one
- **Algorithms Used**:
  - `fuzz.ratio()` - Overall similarity
  - `fuzz.partial_ratio()` - Partial string matching
  - `fuzz.token_sort_ratio()` - Token-based comparison
- **Benefit**: Catches more variations of similar titles

#### **Layer 3: Content Hash Matching**
- **New Feature**: Generates MD5 hash of cleaned content for exact duplicate detection
- **Implementation**: Removes HTML, normalizes whitespace, removes punctuation
- **Benefit**: Detects identical content even with different formatting

#### **Layer 4: Content Similarity Analysis**
- **New Feature**: Compares first 500 characters of article content
- **Threshold**: Configurable (default 80% similarity)
- **Benefit**: Catches articles with same content but different titles

#### **Layer 5: Word Overlap Analysis**
- **New Feature**: Calculates word overlap percentage between titles
- **Threshold**: Configurable (default 70% overlap)
- **Benefit**: Detects semantically similar titles with different wording

### 2. WordPress Integration

#### **Real-time WordPress Checking**
- **New Feature**: Fetches recent WordPress posts via REST API
- **Scope**: Configurable days back (default 7 days)
- **Comparison**: Compares against both titles and content of existing posts
- **Benefit**: Prevents duplicates even if local history is lost

#### **Efficient API Usage**
- **Optimization**: Only fetches necessary fields (`title`, `content`, `link`, `date`)
- **Pagination**: Handles large numbers of posts efficiently
- **Error Handling**: Graceful fallback if WordPress API is unavailable

### 3. Advanced Text Processing

#### **Smart Text Cleaning**
- **HTML Removal**: Strips HTML tags from content
- **Normalization**: Standardizes whitespace and removes punctuation
- **Case Insensitive**: All comparisons are case-insensitive
- **Benefit**: More accurate similarity detection

#### **Multiple Comparison Methods**
- **Exact Matching**: Content hash comparison
- **Fuzzy Matching**: Multiple algorithms for title similarity
- **Semantic Matching**: Word overlap analysis
- **Content Sampling**: First 500 characters for content comparison

### 4. Configurable Parameters

New configuration options in `config.ini`:

```ini
[main]
# Existing settings
similarity_threshold = 85
# New settings
wordpress_check_days = 7
content_similarity_threshold = 80
word_overlap_threshold = 0.7
```

### 5. Enhanced Data Persistence

#### **Structured URL History**
- **Format**: JSON with metadata (URL, title, processed date)
- **Location**: `posted_articles_urls.json`
- **Benefit**: Better tracking and debugging capabilities

#### **Dual Tracking System**
- **Legacy Support**: Maintains existing title-based history file
- **New System**: Adds URL-based tracking
- **Redundancy**: Multiple safeguards against duplicates

## Implementation Details

### Duplicate Detection Flow

1. **URL Check**: Is this URL already processed?
2. **Local Title Check**: Similar to previously posted titles?
3. **Content Fetch**: Get full article content
4. **WordPress Check**: Similar to recent WordPress posts?
5. **AI Rewriting**: Process through AI rewriter
6. **Final Check**: Is rewritten content similar to existing posts?
7. **Post & Track**: If unique, post and save to all tracking systems

### Performance Optimizations

- **Early Termination**: Stops processing at first duplicate detection
- **Efficient API Calls**: Minimal WordPress API requests
- **Smart Caching**: Loads all comparison data once per run
- **Configurable Scope**: Adjustable time windows for checks

### Error Handling

- **Graceful Degradation**: Works even if WordPress API fails
- **Fallback Systems**: Multiple backup duplicate detection methods
- **Comprehensive Logging**: Detailed logging for debugging
- **Safe Defaults**: Conservative thresholds to prevent false positives

## Benefits

### 1. **Comprehensive Coverage**
- Catches duplicates that single-method systems miss
- Works across different content sources and formats
- Handles both exact and near-duplicate content

### 2. **Reliability**
- Multiple redundant systems
- Works even with partial system failures
- Maintains data integrity across restarts

### 3. **Configurability**
- Adjustable thresholds for different use cases
- Configurable time windows
- Flexible similarity criteria

### 4. **Performance**
- Efficient algorithms and data structures
- Minimal external API calls
- Fast local comparisons

### 5. **Maintainability**
- Clear separation of concerns
- Comprehensive logging
- Modular design for easy updates

## Usage

The enhanced system works automatically with the existing workflow. No changes to the main execution command are required:

```bash
python main.py
```

### Monitoring

Check the logs for duplicate detection activity:
- `app.log` - Main application log with duplicate detection details
- `posted_articles.log` - Title history (legacy)
- `posted_articles_urls.json` - URL tracking (new)

### Configuration

Adjust thresholds in `config.ini` based on your needs:
- **Higher thresholds** = More strict (fewer duplicates, might miss some)
- **Lower thresholds** = More lenient (catches more duplicates, might block unique content)

## Testing

A test script is provided to validate the duplicate detection:

```bash
python test_duplicate_detection.py
```

This tests various scenarios including title similarity, content matching, and URL tracking.

## Backward Compatibility

The enhanced system maintains full backward compatibility:
- Existing configuration files work unchanged
- Legacy history files are preserved and used
- All existing functionality remains intact
- Gradual migration to new features

## Future Enhancements

Potential areas for further improvement:
1. **Machine Learning**: Train models on your specific content patterns
2. **Semantic Analysis**: Use NLP libraries for deeper content understanding
3. **Image Comparison**: Compare article images for additional duplicate detection
4. **Source Reliability**: Weight duplicate detection based on source credibility
5. **Performance Monitoring**: Add metrics and performance tracking
