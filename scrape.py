import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_video_links(channel_url, scroll_pause_time=2, max_scrolls=30):
    """Extracts all video links and titles from a YouTube channel using Selenium."""

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

    # Open the channel URL and wait for page to load
    driver.get(channel_url)
    time.sleep(1)

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

    # Scroll to load all videos
    scroll_count = 0
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while scroll_count < max_scrolls:
        print("scrolling...")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )

        if new_height == last_height:
            break  # Stop scrolling when there's no more content to load
        last_height = new_height
        scroll_count += 1

    # Extract video links and titles
    video_elements = driver.find_elements(By.XPATH, '//*[@id="video-title-link"]')
    videos = [
        {"title": element.get_attribute("title"), "url": element.get_attribute("href")}
        for element in video_elements
        if element.get_attribute("href")
    ]

    driver.quit()  # Close browser

    return videos  # Return list of dictionaries with titles and URLs


if __name__ == "__main__":

    # Define channel URL
    channel_url = "https://www.youtube.com/@JoshuaWeissman"

    # Get video URLs and titles
    videos = get_video_links(channel_url)

    # Save results to CSV
    df = pd.DataFrame(videos)
    df.to_csv("output/youtube_videos.csv", index=False)

    print(f"Extracted {len(videos)} videos. Saved to youtube_videos.csv")
