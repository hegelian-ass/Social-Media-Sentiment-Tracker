
from pathlib import Path

import pandas as pd
import gspread


# -----------------------------------------
# FILE PATHS
# -----------------------------------------

ROOT = Path(__file__).resolve().parents[2]

CREDENTIALS = ROOT / "credentials" / "google_credentials.json"

COMMENTS_FILE = (
    ROOT / "src" / "data" / "instagram_comments_analyzed.csv"
)

POSTS_FILE = (
    ROOT / "src" / "data" / "instagram_posts.csv"
)

SPREADSHEET_NAME = "LOP_Sentiment_Tracker"


def main():

    # Check files
    for file in [CREDENTIALS, COMMENTS_FILE, POSTS_FILE]:
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")

    # Read data
    comments = pd.read_csv(COMMENTS_FILE).fillna("")
    posts = pd.read_csv(POSTS_FILE).fillna("")

    # Validate columns
    comment_columns = [
        "post_id", "comment_text", "sentiment",
        "issue", "is_major_criticism"
    ]

    post_columns = [
        "post_id", "post_date", "caption", "likes"
    ]

    for column in comment_columns:
        if column not in comments.columns:
            raise ValueError(f"Missing comment column: {column}")

    for column in post_columns:
        if column not in posts.columns:
            raise ValueError(f"Missing post column: {column}")

    # Connect to Google Sheets
    client = gspread.service_account(filename=str(CREDENTIALS))
    spreadsheet = client.open(SPREADSHEET_NAME)
    sheet = spreadsheet.worksheet("Daily Sheet")

    # Read existing rows
    all_rows = sheet.get_all_values()

    # Daily Sheet structure:
    # Row 4: main headers
    # Row 5: Good / Bad subheaders
    # Row 6 onward: data

    updated = 0
    unmatched = 0

    # Group comments by post
    for post_id, group in comments.groupby("post_id"):

        matching = posts[
            posts["post_id"].astype(str) == str(post_id)
        ]

        if matching.empty:
            print(f"Post not found in posts CSV: {post_id}")
            unmatched += 1
            continue

        post = matching.iloc[0]

        post_date = pd.to_datetime(
            post["post_date"], errors="coerce"
        )

        if pd.isna(post_date):
            print(f"Invalid date for post: {post_id}")
            unmatched += 1
            continue

        date_text = post_date.strftime("%d-%m-%Y")
        caption = str(post["caption"]).strip()

        good_count = int(
            (group["sentiment"] == "Good").sum()
        )

        bad_count = int(
            (group["sentiment"] == "Bad").sum()
        )

        major_mask = (
            group["sentiment"].astype(str).str.lower().eq("bad")
            & group["is_major_criticism"].astype(str).str.lower().isin(
                ["true", "1"]
            )
        )

        major_group = group[major_mask]

        major_comments = (
            major_group["comment_text"]
            .astype(str)
            .head(3)
            .tolist()
        )

        major_bad_text = "\n".join(major_comments)

        major_issues = major_group[
            major_group["issue"].astype(str) != "Other"
        ]["issue"]

        if not major_issues.empty:
            major_issue = major_issues.mode().iloc[0]
        else:
            major_issue = "No major issue"

        # Find matching Instagram row.
        # Existing rows begin at row 6.
        matching_row = None

        for index in range(5, len(all_rows)):

            row = all_rows[index]

            date_cell = row[0] if len(row) > 0 else ""
            platform_cell = row[1] if len(row) > 1 else ""
            post_cell = row[2] if len(row) > 2 else ""

            existing_date = pd.to_datetime(
                date_cell, errors="coerce", dayfirst=True
            )

            if pd.isna(existing_date):
                continue

            if (
                existing_date.strftime("%d-%m-%Y") == date_text
                and platform_cell.strip().lower() == "instagram"
                and post_cell.strip() == caption
            ):
                matching_row = index + 1
                break

        if matching_row is None:
            print(f"No matching Daily Sheet row: {post_id}")
            unmatched += 1
            continue

        # Update only F:I.
        # Do not change date, platform, post, likes, or shares.
        sheet.update(
            range_name=f"F{matching_row}:I{matching_row}",
            values=[[
                good_count,
                bad_count,
                major_bad_text,
                major_issue
            ]]
        )

        print(
            f"Updated post {post_id}: "
            f"Good={good_count}, Bad={bad_count}"
        )

        updated += 1

    print("\nINSTAGRAM GOOGLE SHEETS UPDATE")
    print("--------------------------------")
    print("Posts updated:", updated)
    print("Posts not matched:", unmatched)


if __name__ == "__main__":
    main()
