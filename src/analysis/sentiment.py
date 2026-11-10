
import re
import pandas as pd


# Keywords for basic sentiment detection
POSITIVE_WORDS = [
    "good", "great", "excellent", "amazing", "thank you",
    "appreciate", "support", "well done", "good work",
    "great effort", "keep it up", "proud", "improved"
]

NEGATIVE_WORDS = [
    "bad", "poor", "disappointing", "terrible", "worst",
    "problem", "issue", "no proper", "not working",
    "nothing has changed", "frequent cuts", "too long",
    "lack of", "unavailable", "failure", "unemployment",
    "no water", "no electricity", "no roads"
]

ISSUE_KEYWORDS = {
    "Roads": ["road", "roads", "pothole", "construction", "highway"],
    "Water": ["water", "drinking water", "water supply"],
    "Electricity": ["electricity", "power cut", "power cuts", "electric"],
    "Unemployment": ["unemployment", "jobs", "job", "employment"],
    "Governance": ["government", "administration", "governance"],
    "Public Services": ["hospital", "school", "healthcare", "sanitation"]
}


def clean_text(text):
    """Normalize text for keyword matching."""
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def detect_issue(text):
    """Identify the public issue mentioned in a comment."""

    text = clean_text(text)

    for issue, keywords in ISSUE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return issue

    return "Other"


def analyze_comment(comment):
    """Classify one comment using local keyword rules."""

    text = clean_text(comment)

    positive_score = sum(
        1 for word in POSITIVE_WORDS if word in text
    )

    negative_score = sum(
        1 for word in NEGATIVE_WORDS if word in text
    )

    if positive_score > negative_score:
        sentiment = "Good"

    elif negative_score > positive_score:
        sentiment = "Bad"

    else:
        sentiment = "Neutral"

    issue = detect_issue(text)

    # Major criticism must relate to a public issue
    major = (
        sentiment == "Bad"
        and issue != "Other"
        and len(text.split()) >= 4
    )

    if sentiment == "Good":
        reason = "Positive feedback or appreciation"

    elif sentiment == "Bad":
        reason = "Negative feedback or complaint"

    else:
        reason = "No clear positive or negative keywords"

    return {
        "sentiment": sentiment,
        "issue": issue,
        "reason": reason,
        "is_major_criticism": major
    }


def analyze_dataset(input_file, output_file):
    """Analyse all comments and save the results."""

    df = pd.read_csv(input_file)

    if "comment_text" not in df.columns:
        raise ValueError("Missing comment_text column")

    results = df["comment_text"].apply(analyze_comment)

    results_df = pd.DataFrame(results.tolist())

    final_df = pd.concat(
        [df.reset_index(drop=True), results_df],
        axis=1
    )

    final_df.to_csv(output_file, index=False)

    good = (final_df["sentiment"] == "Good").sum()
    bad = (final_df["sentiment"] == "Bad").sum()
    neutral = (final_df["sentiment"] == "Neutral").sum()

    print("\nLOCAL SENTIMENT ANALYSIS COMPLETED")
    print("----------------------------------")
    print("Total comments:", len(final_df))
    print("Good:", good)
    print("Bad:", bad)
    print("Neutral:", neutral)

    print("\nIssue distribution:")
    print(final_df["issue"].value_counts().to_string())

    print("\nMajor negative comments:")

    major_comments = final_df[
        final_df["is_major_criticism"] == True
    ]

    for _, row in major_comments.head(3).iterrows():
        print("-", row["comment_text"])

    print("\nSaved to:", output_file)

    return final_df


if __name__ == "__main__":
    analyze_dataset(
        "data/cleaned_comments.csv",
        "data/analyzed_comments.csv"
    )
