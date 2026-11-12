
import re
from pathlib import Path

import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

DATA_DIR = Path("src/data")

PLATFORMS = {
    "Instagram": {
        "manual": DATA_DIR / "instagram_comments_manual.csv",
        "posts": DATA_DIR / "instagram_posts.csv",
        "output": DATA_DIR / "instagram_comments_analyzed.csv",
    },
    "Facebook": {
        "manual": DATA_DIR / "facebook_comments_manual.csv",
        "posts": DATA_DIR / "facebook_posts.csv",
        "output": DATA_DIR / "facebook_comments_analyzed.csv",
    },
    "X": {
        "manual": DATA_DIR / "x_comments_manual.csv",
        "posts": DATA_DIR / "x_posts.csv",
        "output": DATA_DIR / "x_comments_analyzed.csv",
    },
}


# =========================================================
# TEXT UTILITIES
# =========================================================

def clean_text(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    value = str(value).lower()
    value = value.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", value).strip()


def contains_any(text, keywords):
    text = clean_text(text)

    for keyword in keywords:
        keyword = clean_text(keyword)

        if not keyword:
            continue

        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def normalize_url(url):
    if not url:
        return ""

    return str(url).split("?")[0].rstrip("/").lower()


def is_emoji_only(value):
    text = str(value or "").strip()

    if not text:
        return False

    without_emoji = re.sub(
        r"[\U0001F000-\U0001FAFF"
        r"\U00002600-\U000027BF"
        r"\uFE0F\u200D\uFE0E]",
        "",
        text
    )

    return not re.search(
        r"[A-Za-z0-9\u0900-\u097F]",
        without_emoji
    )


# =========================================================
# SENTIMENT KEYWORDS
# =========================================================

POSITIVE_WORDS = [
    "good", "great", "excellent", "best", "amazing",
    "well done", "thank you", "thanks", "support",
    "proud", "appreciate", "congratulations",
    "zindabad", "shabash", "very good",
    "hardik shubhkamnaye", "well deserved",
    "happy birthday", "keep it up", "great work",
    "salute", "brilliant", "wonderful", "excellent work",
    "jai hind", "bahut achha", "bohot achha",
    "dhanyawad", "shukriya", "blessings"
]

NEGATIVE_WORDS = [
    "bad", "worst", "shame", "shameful", "failure",
    "corruption", "useless", "disappointed",
    "disappointment", "irresponsible", "negligence",
    "neglect", "unacceptable", "disgusting",
    "not done", "no development", "no action",
    "unfulfilled", "unresolved", "pending",
    "problem", "issue", "galat hua", "galat hai",
    "nahi hua", "nahi kiya", "not received",
    "still waiting", "not working", "poor condition",
    "very poor", "failed", "injustice", "ignored",
    "no response", "not fulfilled", "fraud",
    "scam", "loot", "failure of government"
]

COMPLAINT_PATTERNS = [
    "kuch be nhi howa",
    "kuch bhi nahi hua",
    "kuch bhi nhi hua",
    "kuch nahi hua",
    "kuch nhi hua",
    "abhi tak nahi hua",
    "abhi tak nhi hua",
    "salary increment",
    "salary increase",
    "salary pending",
    "salary delay",
    "salary ka kuch",
    "spos ka kuch",
    "spo salary",
    "spos salary",
    "you said",
    "you promised",
    "promise kiya",
    "bola tha",
    "diwali pr hoga",
    "diwali par hoga",
    "no action taken",
    "still waiting",
    "not resolved",
    "not fulfilled",
    "no response",
    "what happened to",
    "where is the",
    "why has it not",
    "why is it still"
]


# =========================================================
# 25 PUBLIC ISSUE CATEGORIES
# =========================================================

ISSUE_KEYWORDS = {

    "Governance": [
        "government", "administration", "officials",
        "grievance", "pending", "unfulfilled",
        "no action", "no response", "department",
        "authority", "complaint", "promise",
        "promised", "spo", "spos", "salary",
        "increment", "public hearing", "redressal"
    ],

    "Security": [
        "vdg", "village defence", "village defense",
        "security", "terrorism", "terrorist",
        "militant", "militancy", "attack", "firing",
        "crpf", "police deployment", "border security",
        "threat", "encounter", "safety of villagers",
        "weapon"
    ],

    "Infrastructure": [
        "road", "roads", "bridge", "connectivity",
        "construction", "building", "infrastructure",
        "road repair", "highway", "footpath", "culvert"
    ],

    "Employment": [
        "unemployment", "employment", "job", "jobs",
        "recruitment", "vacancy", "vacancies",
        "berozgari", "selection list", "job notification",
        "regularisation", "regularization",
        "daily wager", "appointment order"
    ],

    "Education": [
        "school", "college", "university", "education",
        "teacher", "teachers", "student", "students",
        "scholarship", "examination", "exam", "admission",
        "tuition", "campus", "syllabus", "classroom",
        "hostel"
    ],

    "Healthcare": [
        "hospital", "doctor", "medical", "healthcare",
        "medicine", "ambulance", "patient",
        "health centre", "health center",
        "dispensary", "medical facility",
        "treatment", "blood bank", "nursing staff"
    ],

    "Agriculture": [
        "farmer", "farmers", "agriculture", "crop",
        "crops", "irrigation", "fertilizer",
        "fertiliser", "orchard", "horticulture",
        "apple growers", "agricultural subsidy",
        "mandi", "harvest"
    ],

    "Economy": [
        "inflation", "price rise", "price hike",
        "cost of living", "economic crisis",
        "business loss", "market rates",
        "financial hardship", "small business",
        "traders", "trade", "investment", "industry"
    ],

    "Social Welfare": [
        "pension", "old age pension", "widow pension",
        "disability pension", "financial assistance",
        "welfare scheme", "social security",
        "beneficiary", "benefits", "scheme payment",
        "relief amount"
    ],

    "Women & Child Welfare": [
        "women safety", "women empowerment",
        "child welfare", "child protection",
        "maternity benefit", "anganwadi",
        "anganwadi worker", "domestic violence",
        "girls education", "women employment",
        "maternal health"
    ],

    "Water & Sanitation": [
        "drinking water", "water supply",
        "water shortage", "water scarcity",
        "jal jeevan mission", "sewage", "drainage",
        "sanitation", "toilet", "garbage collection",
        "waste disposal", "tap water", "water connection"
    ],

    "Electricity": [
        "electricity", "power cut", "power cuts",
        "power supply", "transformer", "electric supply",
        "electricity bill", "load shedding", "power outage"
    ],

    "Transport": [
        "public transport", "bus service", "bus",
        "buses", "railway", "train service", "traffic",
        "transport facility", "road transport",
        "passenger service", "transportation"
    ],

    "Tourism": [
        "tourism", "tourist", "tourists",
        "tourist facilities", "tourist destination",
        "hotel industry", "pilgrimage tourism",
        "tourism development", "homestay"
    ],

    "Environment": [
        "pollution", "deforestation", "forest",
        "environment", "climate change",
        "waste management", "plastic pollution",
        "river pollution", "air quality",
        "illegal mining", "wetland", "tree plantation"
    ],

    "Disaster Management": [
        "flood", "floods", "landslide", "landslides",
        "cloudburst", "earthquake", "disaster",
        "relief", "rehabilitation", "rescue operation",
        "disaster relief", "natural calamity"
    ],

    "Housing": [
        "housing", "house construction", "housing scheme",
        "pmay", "pm awas", "displacement",
        "rehabilitation", "homeless", "land allotment",
        "shelter"
    ],

    "Law & Justice": [
        "justice", "court", "judiciary", "legal case",
        "police complaint", "fir", "arrest",
        "investigation", "legal action", "court case",
        "justice delayed", "case hearing"
    ],

    "Corruption & Accountability": [
        "corruption", "bribe", "bribery", "scam",
        "fraud", "misuse of funds",
        "financial irregularities", "accountability",
        "transparency", "embezzlement",
        "commission", "tender irregularity"
    ],

    "Youth Affairs": [
        "youth", "young people", "sports",
        "sports facilities", "skill development",
        "skill training", "youth development",
        "youth engagement", "stadium", "playground"
    ],

    "Rural Development": [
        "rural development", "village development",
        "panchayat", "panchayati raj", "gram sabha",
        "village facilities", "rural connectivity",
        "mgnrega", "mgnregs", "mgnrega wages",
        "block development", "rural area"
    ],

    "Urban Development": [
        "urban development", "municipality",
        "municipal corporation", "municipal council",
        "urban planning", "street lights",
        "public park", "encroachment", "town planning"
    ],

    "Food & Public Distribution": [
        "ration", "ration card", "pds",
        "public distribution system", "food shortage",
        "food grains", "fair price shop",
        "ration supply", "food security"
    ],

    "Culture & Heritage": [
        "heritage", "culture", "cultural heritage",
        "heritage site", "historic monument",
        "preservation", "traditional art",
        "cultural identity", "historical site"
    ]
}


# =========================================================
# ISSUE DESCRIPTIONS
# =========================================================

ISSUE_DESCRIPTIONS = {
    "Governance":
        "Administrative delays, public grievances and unfulfilled commitments",

    "Security":
        "Public safety, local security and protection concerns",

    "Infrastructure":
        "Road connectivity and public infrastructure development",

    "Employment":
        "Unemployment, recruitment delays and job opportunities",

    "Education":
        "Educational facilities, student welfare and academic concerns",

    "Healthcare":
        "Healthcare facilities and availability of medical services",

    "Agriculture":
        "Farmers' concerns and agricultural livelihood",

    "Economy":
        "Economic conditions, rising prices and business concerns",

    "Social Welfare":
        "Pension, welfare schemes and financial assistance",

    "Women & Child Welfare":
        "Women's safety, child welfare and protection services",

    "Water & Sanitation":
        "Drinking water supply, drainage and sanitation facilities",

    "Electricity":
        "Electricity supply and power distribution concerns",

    "Transport":
        "Public transport, traffic and connectivity concerns",

    "Tourism":
        "Tourism development and visitor facilities",

    "Environment":
        "Environmental protection, pollution and waste management",

    "Disaster Management":
        "Disaster preparedness, relief and rehabilitation",

    "Housing":
        "Housing assistance, shelter and rehabilitation",

    "Law & Justice":
        "Legal grievances, police matters and access to justice",

    "Corruption & Accountability":
        "Public accountability and alleged financial irregularities",

    "Youth Affairs":
        "Youth development, sports and skill opportunities",

    "Rural Development":
        "Village development and rural public services",

    "Urban Development":
        "Municipal administration and urban civic facilities",

    "Food & Public Distribution":
        "Ration distribution and public food supply",

    "Culture & Heritage":
        "Cultural heritage protection and preservation",

    "Other":
        "Public concern requiring further review"
}


# =========================================================
# MAJOR ISSUE AND MAJOR CRITICISM RULES
# =========================================================

MAJOR_ISSUE_PATTERNS = [
    "vdg", "village defence", "village defense",
    "spo salary", "spos salary", "salary increment",
    "salary pending", "salary delay",
    "unfulfilled promise", "no action taken",
    "not resolved", "kuch be nhi howa",
    "kuch bhi nahi hua", "diwali pr hoga",
    "diwali par hoga", "road connectivity",
    "water shortage", "power cut", "hospital",
    "ambulance", "recruitment delay"
]

MAJOR_CRITICISM_WORDS = [
    "corruption", "failure", "neglect", "unfulfilled",
    "unresolved", "salary pending", "no action",
    "no development", "shameful", "irresponsible",
    "unacceptable", "disgusting", "not done",
    "nahi hua", "nahi kiya", "kuch be nhi howa",
    "kuch bhi nahi hua", "still waiting",
    "no response", "you promised", "bola tha",
    "diwali pr hoga"
]

SYMPATHY_CONTEXT = [
    "condolence", "demise", "passed away", "death",
    "sad demise", "injured", "injury", "attack",
    "firing", "crpf", "accident", "tragedy",
    "victim", "martyr", "jawans", "soldiers"
]

SAD_EMOJIS = ["😢", "😭", "🥺", "🙏"]


# =========================================================
# ISSUE DETECTION
# =========================================================

def detect_issue_categories(comment):
    categories = []

    for category, keywords in ISSUE_KEYWORDS.items():
        if contains_any(comment, keywords):
            categories.append(category)

    return categories if categories else ["Other"]


def describe_issues(comment, categories):
    text = clean_text(comment)
    descriptions = []

    for category in categories:
        description = ISSUE_DESCRIPTIONS[category]

        # More specific Governance description
        if category == "Governance":
            if contains_any(text, ["spo", "spos", "salary", "increment"]):
                description = (
                    "SPO salary increment delays and unfulfilled demands"
                )
            elif contains_any(text, ["no action", "no response", "pending"]):
                description = (
                    "Pending public grievances and lack of administrative response"
                )
            elif contains_any(text, ["promise", "promised", "bola tha"]):
                description = (
                    "Unfulfilled public commitments and promises"
                )

        # More specific Security description
        if category == "Security":
            if contains_any(text, ["vdg", "village defence", "village defense"]):
                description = (
                    "Demand for Village Defence Guard deployment"
                )
            elif contains_any(text, ["attack", "firing", "militant", "terrorist"]):
                description = (
                    "Local security concerns relating to attacks or violence"
                )

        # More specific Infrastructure description
        if category == "Infrastructure":
            if contains_any(text, ["road", "roads", "connectivity", "bridge"]):
                description = (
                    "Road connectivity and public infrastructure concerns"
                )

        descriptions.append(f"{category}: {description}")

    return "; ".join(descriptions)


def detect_major_issue(comment, categories):
    if contains_any(comment, MAJOR_ISSUE_PATTERNS):
        return True

    if (
        "Security" in categories
        and contains_any(
            comment,
            ["vdg", "village defence", "village defense"]
        )
    ):
        return True

    if (
        "Governance" in categories
        and contains_any(comment, ["spo", "spos", "salary", "increment"])
    ):
        return True

    return False


def detect_major_criticism(comment, sentiment):
    if sentiment != "Bad":
        return False

    return (
        contains_any(comment, COMPLAINT_PATTERNS)
        or contains_any(comment, MAJOR_CRITICISM_WORDS)
    )


# =========================================================
# SENTIMENT ANALYSIS
# =========================================================

def analyse_comment(comment, caption=""):
    original_comment = str(comment or "")
    text = clean_text(original_comment)
    caption = clean_text(caption)

    if not text:
        return {
            "sentiment": "Neutral",
            "issue": "Other",
            "issue_categories": "Other",
            "issue_description": "Other: Public concern requiring review",
            "is_major_criticism": False,
            "is_major_issue": False,
            "major_issue_text": ""
        }

    categories = detect_issue_categories(text)
    issue_description = describe_issues(text, categories)

    major_issue = detect_major_issue(text, categories)

    # Explicit complaints have priority.
    if contains_any(text, COMPLAINT_PATTERNS):
        sentiment = "Bad"

    # Sympathy emojis in condolence/incident posts are supportive.
    elif (
        any(emoji in original_comment for emoji in SAD_EMOJIS)
        and contains_any(caption, SYMPATHY_CONTEXT)
    ):
        sentiment = "Good"

    # Sad emoji-only comments are Neutral, not automatically Good.
    elif is_emoji_only(original_comment):
        if any(emoji in original_comment for emoji in SAD_EMOJIS):
            sentiment = "Neutral"
        else:
            sentiment = "Good"

    else:
        positive = contains_any(text, POSITIVE_WORDS)
        negative = contains_any(text, NEGATIVE_WORDS)

        if positive and negative:
            sentiment = "Neutral"
        elif negative:
            sentiment = "Bad"
        elif positive:
            sentiment = "Good"
        else:
            sentiment = "Neutral"

    major_criticism = detect_major_criticism(text, sentiment)

    # Column I format:
    # Category: issue description — "original supporting comment"
    major_issue_text = ""

    if major_issue:
        evidence = original_comment.strip().replace('"', "'")
        major_issue_text = (
            f'{issue_description} — "{evidence}"'
        )

    return {
        "sentiment": sentiment,
        "issue": categories[0],
        "issue_categories": "; ".join(categories),
        "issue_description": issue_description,
        "is_major_criticism": bool(major_criticism),
        "is_major_issue": bool(major_issue),
        "major_issue_text": major_issue_text
    }


# =========================================================
# CSV LOADING
# =========================================================

def load_csv(path, required_columns):
    if not path.exists():
        print(f"SKIPPED: File not found: {path}")
        return None

    frame = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

    missing = [
        column for column in required_columns
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            f"{path} is missing required columns: {missing}"
        )

    return frame


# =========================================================
# PLATFORM ANALYSIS
# =========================================================

def analyse_platform(platform, config):

    manual = load_csv(
        config["manual"],
        ["post_id", "post_url", "comment_id", "comment_text"]
    )

    posts = load_csv(
        config["posts"],
        ["post_url", "caption"]
    )

    if manual is None or posts is None:
        return None

    caption_map = {}

    for _, post in posts.iterrows():
        url = normalize_url(post.get("post_url", ""))

        if url:
            caption_map[url] = post.get("caption", "")

    results = []

    for _, row in manual.iterrows():
        post_url = normalize_url(row.get("post_url", ""))
        caption = caption_map.get(post_url, "")

        result = analyse_comment(
            row.get("comment_text", ""),
            caption
        )

        results.append(result)

    result_frame = manual.copy()

    result_frame["platform"] = platform

    output_columns = [
        "sentiment",
        "issue",
        "issue_categories",
        "issue_description",
        "is_major_criticism",
        "is_major_issue",
        "major_issue_text"
    ]

    for column in output_columns:
        result_frame[column] = [
            result[column] for result in results
        ]

    config["output"].parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result_frame.to_csv(
        config["output"],
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 45)
    print(platform, "ANALYSIS")
    print("=" * 45)

    print("Total comments:", len(result_frame))

    for sentiment in ["Good", "Bad", "Neutral"]:
        count = int(
            (result_frame["sentiment"] == sentiment).sum()
        )
        print(f"{sentiment}: {count}")

    print(
        "Major criticism:",
        int(result_frame["is_major_criticism"].sum())
    )

    print(
        "Major public issues:",
        int(result_frame["is_major_issue"].sum())
    )

    print("Saved:", config["output"])

    return result_frame


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 55)
    print("MULTI-PLATFORM SENTIMENT ANALYSIS")
    print("Instagram + Facebook + X")
    print("=" * 55)

    all_results = []

    for platform, config in PLATFORMS.items():

        try:
            result = analyse_platform(platform, config)

            if result is not None:
                all_results.append(result)

        except Exception as error:
            print(f"\nERROR in {platform}: {error}")

    if not all_results:
        print("\nNo platform files were successfully analysed.")
        return

    combined = pd.concat(
        all_results,
        ignore_index=True
    )

    combined_path = (
        DATA_DIR / "all_platforms_comments_analyzed.csv"
    )

    combined_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    combined.to_csv(
        combined_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 55)
    print("COMBINED ANALYSIS COMPLETED")
    print("=" * 55)

    print("Total comments:", len(combined))
    print("Combined file:", combined_path)


if __name__ == "__main__":
    main()
