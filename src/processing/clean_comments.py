
import pandas as pd
import re


def clean_comment(comment):
    """Clean an individual social media comment."""

    if pd.isna(comment):
        return ""

    comment = str(comment)

    # Remove URLs
    comment = re.sub(r"https?://\S+|www\.\S+", "", comment)

    # Remove unnecessary spaces and line breaks
    comment = re.sub(r"\s+", " ", comment)

    return comment.strip()


def clean_dataset(input_file, output_file):
    """Load, clean and save social media comments."""

    df = pd.read_csv(input_file)

    if "comment_text" not in df.columns:
        raise ValueError("Dataset must contain comment_text column")

    df["comment_text"] = df["comment_text"].apply(clean_comment)

    # Remove empty comments
    df = df[df["comment_text"] != ""]

    # Remove duplicate comment IDs
    if "comment_id" in df.columns:
        df = df.drop_duplicates(subset=["comment_id"])

    df.to_csv(output_file, index=False)

    print("Comment cleaning completed!")
    print("Total comments:", len(df))

    return df


if __name__ == "__main__":
    clean_dataset(
        "data/sample_comments.csv",
        "data/cleaned_comments.csv"
    )
