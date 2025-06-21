import openai
import boto3
from openai import OpenAI
import re
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Set API keys and secrets using environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
S3_REGION = "eu-west-2"  # e.g., us-east-1
AWS_KEY_ID = os.getenv("AWS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def extract_s3_filename(image_url: str) -> str:
    """Extract the filename from the S3 image URL."""
    parsed_url = urlparse(image_url)
    return parsed_url.path.lstrip("/")  # remove leading /


def get_caption_for_image(filename, bucket_name):
    client = boto3.client(
        "rekognition",
        aws_access_key_id=AWS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=S3_REGION,
    )

    try:
        response = client.detect_labels(
            Image={"S3Object": {"Bucket": bucket_name, "Name": filename}},
            MaxLabels=10,
        )
        print("Detected labels for " + filename)
        labels = response["Labels"]
        label_name_list = []
        for label in labels:
            label_name_list.append(label["Name"])
            print("Label: " + label["Name"])
            print("Confidence: " + str(label["Confidence"]))
        return label_name_list
    except Exception as e:
        return {"statusCode": 500, "error": str(e)}


def generate_content_from_image_labels(
    caption_1, caption_2, caption_3, theme=None, content_type="story"
):
    client = OpenAI(api_key=openai.api_key)
    print("Generating content from labels")

    theme_text = f" Write it in the theme of '{theme}'." if theme else ""

    prompt = (
        f"Write a short {content_type} of no more than 50 words that includes these elements: "
        f"{caption_1}, {caption_2}, and {caption_3}.{theme_text} "
        f"Generate a title for the {content_type} in 5 words or less."
    )

    try:
        career = "poet" if content_type == "poem" else "author"
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a children's {career} skilled in adventure, fantasy, "
                    "and emotional creative writing for ages 8 to 16.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        generated_content = completion.choices[0].message.content
        print("Content generated from openAI API")

        # Use regex to extract title and body reliably
        title_match = re.search(r"^Title:\s*(.*)", generated_content)
        title = (
            title_match.group(1).strip() if title_match else f"Untitled {content_type}"
        )

        # Remove the title line from content
        content = re.sub(r"^Title:.*\n?", "", generated_content).strip()

        return {"title": title, f"{content_type}": content}

    except Exception as e:
        return {"statusCode": 500, "error": str(e)}
