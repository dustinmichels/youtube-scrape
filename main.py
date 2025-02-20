import pandas as pd

from scrape import get_video_links
from transcript import get_transcript


def main():
    # Define channel URL
    channel_url = "https://www.youtube.com/@JoshuaWeissman"

    # Get video URLs and titles
    videos = get_video_links(channel_url)

    output_list = []

    # Get transcript for each video
    for video in videos[0:3]:
        print(f"Getting transcript for '{video['title']}'...")

        # get id from url
        video_id = video["url"].split("v=")[1]

        try:
            transcript = get_transcript(video_id)
        except Exception as e:
            print(f"Error getting transcript for '{video['title']}': {e}")
            transcript = None

        output_list.append(
            {"title": video["title"], "url": video["url"], "transcript": transcript}
        )

    # save to csv
    df = pd.DataFrame(output_list)
    df.to_csv("output/youtube_videos.csv", index=False)


if __name__ == "__main__":
    main()
    print("Done.")
