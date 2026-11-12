
import instaloader
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

USERNAME = "sunilsharmabjpofficial"
START_DATE = datetime(2026, 11, 6, tzinfo=timezone.utc)

OUTPUT_FILE = Path("data/instagram_posts.csv")
COMMENTS_FILE = Path("data/instagram_comments.csv")


def collect_posts():
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        compress_json=False
    )

    print(f"Checking public posts for @{USERNAME}...")

    try:
        profile = instaloader.Profile.from_username(
            loader.context, USERNAME
        )

        posts = []
        all_comments = []

        for post in profile.get_posts():

            post_date = post.date_utc.replace(
                tzinfo=timezone.utc
            )

            # Stop when posts are older than the start date.
            if post_date < START_DATE:
                break

            print(f"Collecting post: {post.shortcode}")

            # Attempt to collect accessible comments.
            try:
                for comment in post.get_comments():
                    all_comments.append({
                        "platform": "Instagram",
                        "post_id": post.mediaid,
                        "post_date": post_date.isoformat(),
                        "post_url": (
                            f"https://www.instagram.com/p/{post.shortcode}/"
                        ),
                        "comment_id": comment.id,
                        "comment_text": comment.text,
                        "comment_date": (
                            comment.created_at_utc.isoformat()
                        ),
                        "username": comment.owner.username
                    })

            except Exception as error:
                print(
                    f"Could not collect comments for post "
                    f"{post.mediaid}: {error}"
                )

            # Save post details.
            posts.append({
                "platform": "Instagram",
                "username": USERNAME,
                "post_id": post.mediaid,
                "post_date": post_date.isoformat(),
                "caption": post.caption or "",
                "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
                "likes": post.likes,
                "comments_count": post.comments,
                "is_video": post.is_video
            })

        # Create output folders.
        OUTPUT_FILE.parent.mkdir(
            parents=True, exist_ok=True
        )

        # Save post metadata.
        posts_df = pd.DataFrame(
            posts,
            columns=[
                "platform",
                "username",
                "post_id",
                "post_date",
                "caption",
                "post_url",
                "likes",
                "comments_count",
                "is_video"
            ]
        )

        posts_df.to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        # Define comment CSV columns.
        comments_columns = [
            "platform",
            "post_id",
            "post_date",
            "post_url",
            "comment_id",
            "comment_text",
            "comment_date",
            "username"
        ]

        # Save comments, even if none were accessible.
        comments_df = pd.DataFrame(
            all_comments,
            columns=comments_columns
        )

        comments_df.to_csv(
            COMMENTS_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        print("\nINSTAGRAM COLLECTION COMPLETED")
        print("Posts collected:", len(posts_df))
        print("Comments collected:", len(comments_df))
        print("Posts saved to:", OUTPUT_FILE)
        print("Comments saved to:", COMMENTS_FILE)

    except Exception as error:
        print("\nInstagram collection failed.")
        print("Reason:", error)
        print("Instagram may restrict automated public access.")


if __name__ == "__main__":
    collect_posts()
