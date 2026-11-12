
import pandas as pd
import gspread
from pathlib import Path

# Find the project root automatically
ROOT = Path(__file__).resolve().parents[2]

# File locations
CSV_FILE = ROOT / "src" / "data" / "instagram_posts.csv"
CREDENTIALS_FILE = ROOT / "credentials" / "google_credentials.json"

# Connect to Google Sheets
client = gspread.service_account(
    filename=str(CREDENTIALS_FILE)
)

spreadsheet = client.open("LOP_Sentiment_Tracker")
worksheet = spreadsheet.worksheet("Daily Sheet")


def normalise_date(value):
    parsed = pd.to_datetime(
        value,
        dayfirst=True,
        errors="coerce",
        utc=True
    )

    if pd.isna(parsed):
        return ""

    return parsed.strftime("%Y-%m-%d")


def upload_instagram_posts():

    # Check whether the CSV file exists
    if not CSV_FILE.exists():
        print("Instagram posts CSV not found:", CSV_FILE)
        return

    # Read Instagram posts
    df = pd.read_csv(CSV_FILE).fillna("")

    if df.empty:
        print("No Instagram posts available.")
        return

    # Sort posts from oldest to newest
    df["post_date"] = pd.to_datetime(
        df["post_date"],
        utc=True,
        errors="coerce"
    )

    df = df.sort_values(
        by="post_date",
        ascending=True
    )

    # Read existing Google Sheet records
    existing_values = worksheet.get_all_values()

    # Existing records begin at row 6
    existing_posts = set()

    for row in existing_values[5:]:
        if len(row) >= 3:
            key = (
                normalise_date(row[0]),
                row[1].strip().lower(),
                row[2].strip()
            )
            existing_posts.add(key)

    # Prepare new Instagram rows
    new_rows = []

    for _, post in df.iterrows():

        post_date = normalise_date(post["post_date"])
        platform = "Instagram"
        caption = str(post["caption"]).strip()

        key = (
            post_date,
            platform.lower(),
            caption
        )

        # Skip records already present
        if key in existing_posts:
            continue

        likes = post["likes"]

        new_rows.append([
            pd.to_datetime(post_date).strftime("%d/%m/%Y")
            if post_date else "",
            platform,
            caption,
            likes,
            "",  # Shares unavailable
            "",  # Good comments not yet analysed
            "",  # Bad comments not yet analysed
            "",  # Major bad comments not yet analysed
            ""   # Major issue not yet analysed
        ])

        existing_posts.add(key)

    # Upload new rows
    if new_rows:
        worksheet.append_rows(
            new_rows,
            value_input_option="USER_ENTERED"
        )

        print("\nDaily Sheet updated successfully!")
        print("New Instagram posts uploaded:", len(new_rows))
    else:
        print("No new Instagram posts to upload.")


if __name__ == "__main__":
    upload_instagram_posts()
