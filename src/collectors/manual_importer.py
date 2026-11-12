
from pathlib import Path
import pandas as pd


# Project paths
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "src" / "data"


# Excel inputs and CSV outputs
PLATFORMS = {
    "facebook": {
        "posts_input": "facebook_posts.xlsx",
        "comments_input": "facebook_comments_manual.xlsx",
        "posts_output": "facebook_posts.csv",
        "comments_output": "facebook_comments_manual.csv",
    },
    "x": {
        "posts_input": "x_posts.xlsx",
        "comments_input": "x_comments_manual.xlsx",
        "posts_output": "x_posts.csv",
        "comments_output": "x_comments_manual.csv",
    },
}


POST_COLUMNS = [
    "platform",
    "post_date",
    "caption",
    "post_url",
    "likes",
    "comments_count",
    "is_video",
]

COMMENT_COLUMNS = [
    "post_id",
    "post_url",
    "comment_id",
    "comment_text",
]


def read_excel_file(filename):
    """Read an Excel input and verify that it exists."""
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    return pd.read_excel(file_path)


def validate_columns(df, required_columns, filename):
    """Check that all required columns are present."""
    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{filename} is missing required columns: {missing}"
        )


def convert_platform(platform, config):
    """Convert one platform's Excel inputs into CSV files."""
    posts = read_excel_file(config["posts_input"])
    comments = read_excel_file(config["comments_input"])

    validate_columns(
        posts,
        POST_COLUMNS,
        config["posts_input"],
    )

    validate_columns(
        comments,
        COMMENT_COLUMNS,
        config["comments_input"],
    )

    # Keep only columns supported by the existing sentiment pipeline.
    posts = posts[POST_COLUMNS].copy()
    comments = comments[COMMENT_COLUMNS].copy()

    # Set the correct platform label.
    posts["platform"] = platform

    # Do not overwrite existing output files with empty inputs.
    if posts.empty or comments.empty:
        print(
            f"SKIPPED {platform}: "
            "posts or comments input is empty. "
            "Existing CSV outputs were not changed."
        )
        return

    posts_output = DATA_DIR / config["posts_output"]
    comments_output = DATA_DIR / config["comments_output"]

    posts.to_csv(posts_output, index=False, encoding="utf-8-sig")
    comments.to_csv(comments_output, index=False, encoding="utf-8-sig")

    print(
        f"SUCCESS {platform}: "
        f"{len(posts)} posts and {len(comments)} comments converted."
    )


def main():
    print("=" * 55)
    print("MULTI-PLATFORM MANUAL IMPORTER")
    print("=" * 55)

    for platform, config in PLATFORMS.items():
        try:
            convert_platform(platform, config)
        except Exception as error:
            print(f"ERROR {platform}: {error}")

    print("=" * 55)
    print("IMPORTER FINISHED")
    print("=" * 55)


if __name__ == "__main__":
    main()
