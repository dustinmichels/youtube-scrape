import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_video_links(channel_url, scroll_pause_time=2, max_scrolls=30):
    """Extracts all video links from a YouTube channel using Selenium."""

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    chrome_options.add_argument("--mute-audio")  # Mute audio for faster load

    # Start WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the YouTube channel videos page
    if "/videos" not in channel_url:
        channel_url = channel_url.rstrip("/") + "/videos"

    driver.get(channel_url)
    time.sleep(1)  # Wait for page to load

    # Wait and click the "Accept all" button if it appears
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//span[contains(text(), "Accept all")]')
            )
        )
        accept_button.click()
        print("Clicked 'Accept all' button.")
    except:
        print("Consent button not found or already accepted.")

    # Continue with the rest of the script
    print("Current URL after consent:", driver.current_url)

    print("Current URL:", driver.current_url)
    print("Page Title:", driver.title)

    # Scroll to load all videos
    scroll_count = 0
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while scroll_count < max_scrolls:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )

        if new_height == last_height:
            break  # Stop scrolling when there's no more content to load
        last_height = new_height
        scroll_count += 1

    all_links = [
        a.get_attribute("href") for a in driver.find_elements(By.TAG_NAME, "a")
    ]
    print(all_links)  # Debugging: See all links found

    # Extract video links
    video_elements = driver.find_elements(By.XPATH, '//*[@id="video-title-link"]')
    video_links = [
        element.get_attribute("href")
        for element in video_elements
        if element.get_attribute("href")
    ]

    driver.quit()  # Close browser

    return list(set(video_links))  # Remove duplicates


# Define channel URL
channel_url = "https://www.youtube.com/@JoshuaWeissman"

# Get video URLs
video_urls = get_video_links(channel_url)

# Save results to CSV
df = pd.DataFrame(video_urls, columns=["Video URL"])
df.to_csv("youtube_videos.csv", index=False)

print(f"Extracted {len(video_urls)} video URLs. Saved to youtube_videos.csv")
