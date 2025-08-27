"""
JavaScript Batch Data Extraction for Parenta Scraper
Fast DOM operations using single JavaScript execution instead of multiple Selenium calls
"""
import time

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


def extract_all_posts_with_carousel_images_js(driver, newsfeed_selector):
    """
    JavaScript-based carousel image extraction with clicking fallback for incomplete carousels
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
            
            // Enhanced robust image extraction for carousels
            let all_image_urls = new Set();
            
            // Method 1: Get all currently visible images with expanded attribute search
            const visibleImages = container.querySelectorAll('img');
            visibleImages.forEach(img => {
                const possibleSources = [
                    img.src,
                    img.getAttribute('data-src'),
                    img.getAttribute('data-original'),
                    img.getAttribute('data-lazy'),
                    img.getAttribute('data-image'),
                    img.getAttribute('ng-src'),
                    img.getAttribute('x-src'),
                    img.getAttribute('data-lazy-src'),
                    img.getAttribute('data-srcset')?.split(' ')[0], // First URL from srcset
                    img.currentSrc
                ];
                
                possibleSources.forEach(src => {
                    if (src && src.startsWith('http') && src.includes('storage101.lon3.clouddrive.com')) {
                        // Clean up URL parameters that might cause duplicates
                        const cleanUrl = src.split('?')[0];
                        all_image_urls.add(cleanUrl);
                    }
                });
            });
            
            // Method 2: Check for carousel indicators and try to extract all images
            const circleDots = container.querySelectorAll('div[data-id*="circle-icon"]');
            
            // Method 3: Deep DOM search for hidden carousel images
            if (circleDots.length > 1) {
                // This is a carousel - use multiple extraction strategies
                
                // Strategy A: Look for carousel containers and slide elements
                const carouselContainers = container.querySelectorAll('[class*="carousel"], [class*="slide"], [class*="gallery"], [data-id*="carousel"], [data-id*="slide"]');
                carouselContainers.forEach(carouselContainer => {
                    const hiddenImages = carouselContainer.querySelectorAll('img');
                    hiddenImages.forEach(img => {
                        const possibleSources = [
                            img.src, img.getAttribute('data-src'), img.getAttribute('data-original'),
                            img.getAttribute('data-lazy'), img.getAttribute('data-image'), img.getAttribute('ng-src'),
                            img.getAttribute('x-src'), img.getAttribute('data-lazy-src'), img.currentSrc
                        ];
                        
                        possibleSources.forEach(src => {
                            if (src && src.startsWith('http') && src.includes('storage101.lon3.clouddrive.com')) {
                                const cleanUrl = src.split('?')[0];
                                all_image_urls.add(cleanUrl);
                            }
                        });
                    });
                });
                
                // Strategy B: Search for inline styles with background images
                const elementsWithBg = container.querySelectorAll('*');
                elementsWithBg.forEach(elem => {
                    const style = elem.getAttribute('style') || '';
                    const bgImageMatch = style.match(/background-image:\\s*url\\(['"]?(https:\\/\\/storage101\\.lon3\\.clouddrive\\.com[^'")]+)/);
                    if (bgImageMatch) {
                        const cleanUrl = bgImageMatch[1].split('?')[0];
                        all_image_urls.add(cleanUrl);
                    }
                });
                
                // Strategy C: Look for JSON data in script tags or data attributes
                const scripts = container.querySelectorAll('script');
                scripts.forEach(script => {
                    const content = script.textContent || script.innerHTML;
                    if (content) {
                        // Enhanced regex to catch more URL patterns
                        const urlPatterns = [
                            /https:\\/\\/storage101\\.lon3\\.clouddrive\\.com[^"'\\s,\\])}]+/g,
                            /"url":\\s*"(https:\\/\\/storage101\\.lon3\\.clouddrive\\.com[^"]+)"/g,
                            /'url':\\s*'(https:\\/\\/storage101\\.lon3\\.clouddrive\\.com[^']+)'/g,
                            /src['"\\s*:\\s*['"](https:\\/\\/storage101\\.lon3\\.clouddrive\\.com[^'"]+)['"]/g
                        ];
                        
                        urlPatterns.forEach(pattern => {
                            const matches = content.matchAll(pattern);
                            for (const match of matches) {
                                const url = match[1] || match[0];
                                if (url) {
                                    const cleanUrl = url.split('?')[0];
                                    all_image_urls.add(cleanUrl);
                                }
                            }
                        });
                    }
                });
                
                // Strategy D: Deep search of all data attributes across all elements
                const allElements = container.querySelectorAll('*');
                allElements.forEach(elem => {
                    const dataAttrs = elem.getAttributeNames()
                        .filter(attr => attr.startsWith('data-'))
                        .map(attr => elem.getAttribute(attr));
                    
                    dataAttrs.forEach(attr => {
                        if (attr && typeof attr === 'string' && attr.includes('storage101.lon3.clouddrive.com')) {
                            const urlMatches = attr.match(/https:\\/\\/storage101\\.lon3\\.clouddrive\\.com[^"'\\s,\\])}]+/g);
                            if (urlMatches) {
                                urlMatches.forEach(url => {
                                    const cleanUrl = url.split('?')[0];
                                    all_image_urls.add(cleanUrl);
                                });
                            }
                        }
                    });
                });
                
                // Strategy E: Look for React/Angular state or props that might contain image arrays
                try {
                    const reactFiber = container._reactInternalFiber || container.__reactInternalInstance;
                    if (reactFiber) {
                        const stateStr = JSON.stringify(reactFiber);
                        const urlMatches = stateStr.match(/https:\\/\\/storage101\\.lon3\\.clouddrive\\.com[^"'\\s,\\])}]+/g);
                        if (urlMatches) {
                            urlMatches.forEach(url => {
                                const cleanUrl = url.split('?')[0];
                                all_image_urls.add(cleanUrl);
                            });
                        }
                    }
                } catch (e) {
                    // React inspection failed, continue
                }
            }
            
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
                image_urls: Array.from(all_image_urls),
                container_index: index,
                has_carousel: circleDots.length > 1,
                carousel_count: circleDots.length
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
                container_index: index,
                has_carousel: false,
                carousel_count: 0
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
        
        # Check each post for carousel fallback needs
        enhanced_data = []
        for i, post in enumerate(valid_data):
            if post.get('has_carousel') and post.get('carousel_count', 0) > len(post.get('image_urls', [])):
                # Carousel detected but insufficient images found - use clicking fallback
                print(f"Carousel fallback needed for post {i}: expected {post.get('carousel_count')} images, found {len(post.get('image_urls', []))}")
                
                try:
                    clicked_images = extract_carousel_images_by_clicking(driver, newsfeed_selector, i)
                    if clicked_images and len(clicked_images) > len(post.get('image_urls', [])):
                        print(f"Clicking fallback successful: found {len(clicked_images)} images")
                        post['image_urls'] = clicked_images
                        post['fallback_used'] = True
                    else:
                        print(f"Clicking fallback did not improve results")
                        post['fallback_used'] = False
                except Exception as fallback_error:
                    print(f"Clicking fallback failed: {fallback_error}")
                    post['fallback_used'] = False
            else:
                post['fallback_used'] = False
            
            enhanced_data.append(post)
        
        return enhanced_data
        
    except Exception as e:
        print(f"JavaScript carousel extraction failed: {e}")
        return extract_all_posts_javascript(driver, newsfeed_selector)


def extract_carousel_images_by_clicking(driver, container_selector, container_index):
    """
    Fallback method: Click through carousel circles to extract all images
    """
    try:
        # Find the specific container
        containers = driver.find_elements("css selector", container_selector)
        if container_index >= len(containers):
            return []
        
        container = containers[container_index]
        
        # Check for circle navigation dots
        circle_dots = container.find_elements("css selector", "div[data-id*='circle-icon']")
        
        if len(circle_dots) <= 1:
            # No carousel, just get current images
            images = container.find_elements("css selector", "img")
            image_urls = []
            for img in images:
                src = img.get_attribute('src') or img.get_attribute('data-src')
                if src and src.startswith('http') and 'storage101.lon3.clouddrive.com' in src:
                    image_urls.append(src)
            return image_urls
        
        # Has carousel - click through each circle
        all_image_urls = set()
        
        for i, circle in enumerate(circle_dots):
            try:
                # Click the circle
                driver.execute_script("arguments[0].click();", circle)
                time.sleep(0.2)  # Wait for image to load
                
                # Get the currently visible image
                images = container.find_elements("css selector", "img")
                for img in images:
                    src = img.get_attribute('src') or img.get_attribute('data-src')
                    if src and src.startswith('http') and 'storage101.lon3.clouddrive.com' in src:
                        all_image_urls.add(src)
                        
            except Exception as e:
                print(f"Error clicking circle {i}: {e}")
                continue
        
        return list(all_image_urls)
        
    except Exception as e:
        print(f"Error in carousel clicking extraction: {e}")
        return []