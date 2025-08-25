"""
JavaScript Batch Data Extraction for Parenta Scraper
Fast DOM operations using single JavaScript execution instead of multiple Selenium calls
"""

def extract_all_posts_javascript(driver, newsfeed_selector):
    """
    Extract all post data using a single JavaScript execution
    50-100x faster than individual Selenium DOM operations
    """
    javascript_code = """
    // Get all containers
    const containers = document.querySelectorAll(arguments[0]);
    
    // Extract data from all containers in one pass
    return Array.from(containers).map((container, index) => {
        try {
            // Extract container ID
            const id = container.getAttribute('data-id') || container.id || `container_${index}`;
            
            // Extract date - try Parenta-specific selectors first
            let date = '';
            const dateSelectors = [
                'div[data-id="newsfeed-event-date"]',
                '[data-reactid*="date"]',
                '.date',
                '[class*="date"]',
                'time',
                '.timestamp'
            ];
            for (const selector of dateSelectors) {
                const dateElem = container.querySelector(selector);
                if (dateElem && dateElem.textContent.trim()) {
                    date = dateElem.textContent.trim();
                    break;
                }
            }
            
            // Extract time - try Parenta-specific selectors first
            let time = '';
            const timeSelectors = [
                'span[data-id="newsfeed-event-time-mobile-only"]',
                '[data-reactid*="time"]',
                '.time',
                '[class*="time"]',
                '.timestamp time'
            ];
            for (const selector of timeSelectors) {
                const timeElem = container.querySelector(selector);
                if (timeElem && timeElem.textContent.trim()) {
                    time = timeElem.textContent.trim();
                    break;
                }
            }
            
            // Extract event type - try Parenta-specific selectors first
            let event_type = '';
            const eventSelectors = [
                'span[data-id="newsfeed-event-type"]',
                '[data-reactid*="event"]',
                '.event-type',
                '[class*="event"]',
                'h1', 'h2', 'h3',
                '.title',
                '[class*="title"]'
            ];
            for (const selector of eventSelectors) {
                const eventElem = container.querySelector(selector);
                if (eventElem && eventElem.textContent.trim()) {
                    event_type = eventElem.textContent.trim();
                    break;
                }
            }
            
            // Extract all image URLs - filter for Parenta storage URLs
            const images = container.querySelectorAll('img');
            const image_urls = Array.from(images)
                .map(img => img.src || img.getAttribute('data-src'))
                .filter(src => src && src.startsWith('http'))
                .filter(src => !src.includes('data:image')) // Skip base64 images
                .filter(src => !src.endsWith('.svg')) // Skip SVG files
                .filter(src => src.includes('storage101.lon3.clouddrive.com')) // Parenta storage only
                .filter((src, index, arr) => arr.indexOf(src) === index); // Remove duplicates
            
            // Extract content text - try Parenta-specific selectors first
            let content = '';
            const contentSelectors = [
                'span[data-id="newsfeed-event-title"]',
                'p',
                '.content',
                '[class*="content"]',
                '.description',
                '[class*="description"]',
                '.text',
                '[class*="text"]'
            ];
            for (const selector of contentSelectors) {
                const contentElems = container.querySelectorAll(selector);
                if (contentElems.length > 0) {
                    content = Array.from(contentElems)
                        .map(elem => elem.textContent.trim())
                        .filter(text => text.length > 0)
                        .join(' ');
                    if (content) break;
                }
            }
            
            return {
                id: id,
                date: date,
                time: time,
                event_type: event_type,
                content: content,
                image_urls: image_urls,
                container_index: index
            };
            
        } catch (error) {
            console.log(`Error extracting data from container ${index}:`, error);
            return {
                id: `error_container_${index}`,
                date: '',
                time: '',
                event_type: 'extraction_error',
                content: `Error: ${error.message}`,
                image_urls: [],
                container_index: index
            };
        }
    });
    """
    
    try:
        # Execute JavaScript and get all data at once
        all_data = driver.execute_script(javascript_code, newsfeed_selector)
        
        # Filter out empty/invalid entries
        valid_data = [
            post for post in all_data 
            if post and post.get('id') and post.get('id') != 'error_container_0'
        ]
        
        return valid_data
        
    except Exception as e:
        print(f"JavaScript batch extraction failed: {e}")
        return []


def get_selectors_from_constants():
    """
    Return the selectors that should be used based on the main script constants
    """
    return {
        'NEWSFEED_ITEM_SELECTOR': 'div[data-id*="newsfeed-event-wrapper"]',
        'DATE_SELECTOR': 'div[data-id="newsfeed-event-date"]',
        'TIME_SELECTOR': 'span[data-id="newsfeed-event-time-mobile-only"]',
        'CONTENT_SELECTOR': 'span[data-id="newsfeed-event-title"]',
        'EVENT_TYPE_SELECTOR': 'span[data-id="newsfeed-event-type"]'
    }