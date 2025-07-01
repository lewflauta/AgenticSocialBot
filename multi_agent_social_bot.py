import os
import asyncio
import datetime
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2 import service_account
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers, TResponseInputItem, trace

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Transcript fetcher
def fetch_transcript(video_id: str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

# Content generator
tool_openai = OpenAI(api_key=OPENAI_API_KEY)

@function_tool
def generate_post(transcript: str, platform: str):
    response = tool_openai.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": "You are a social media content expert."},
            {"role": "user", "content": f"Create a {platform} post using this transcript: {transcript}"}
        ],
        max_output_tokens=2500
    )
    return response.output_text

# Writer agent
writer_agent = Agent(
    name="WriterAgent",
    instructions="Write engaging posts based on a video transcript.",
    model="gpt-4o-mini",
    tools=[WebSearchTool(), generate_post],
    output_type=str,
)

# Evaluator
@dataclass
class EvaluationFeedback:
    feedback: str
    score: int

evaluator_agent = Agent[None](
    name="CriticAgent",
    instructions="Evaluate a social media post's effectiveness and provide a score and feedback.",
    output_type=EvaluationFeedback,
)

# Google setup
SERVICE_ACCOUNT_FILE = "social-media-agent.json"
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/calendar"]
DRIVE_FOLDER_ID = "ENTER YOUR GOOGLEDRIVE ID"

def setup_google():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds), build("calendar", "v3", credentials=creds)

drive_service, calendar_service = setup_google()

# Storage
@dataclass
class StoredPost:
    platform: str
    filename: str
    filelink: str

@dataclass
class StoredPosts:
    posts: List[StoredPost]

@function_tool
def save_post(content: str, filename: str):
    metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID], "mimeType": "text/plain"}
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    file = drive_service.files().create(body=metadata, media_body=media, fields='id, webViewLink').execute()
    return file.get('webViewLink')

storage_agent = Agent(
    name="StorageAgent",
    instructions="Save posts to Google Drive.",
    model="gpt-4o-mini",
    tools=[save_post],
    output_type=StoredPosts,
)

# Scheduler
@function_tool
def current_amsterdam_time():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))

@function_tool
def add_event(title: str, description: str, time_str: str):
    dt = datetime.datetime.fromisoformat(time_str)
    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': dt.isoformat(), 'timeZone': 'Europe/Amsterdam'},
        'end': {'dateTime': (dt + datetime.timedelta(hours=1)).isoformat(), 'timeZone': 'Europe/Amsterdam'},
        'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 60}, {'method': 'popup', 'minutes': 15}]},
    }
    result = calendar_service.events().insert(calendarId='youremail@gmail.com', body=event).execute()
    return result.get("htmlLink")

scheduler_agent = Agent(
    name="SchedulerAgent",
    instructions="Schedule posts on the calendar in the afternoon on weekdays.",
    model="gpt-4o-mini",
    tools=[current_amsterdam_time, add_event],
)

# Main runner
async def main():
    video_id = input("Please enter a youtube video id :")
    transcript = fetch_transcript(video_id)
    prompt = f"Create a LinkedIn and Instagram post based on this transcript: {transcript}"
    input_items = [{"content": prompt, "role": "user"}]

    with trace("Write and critique"):
        content_result = await Runner.run(writer_agent, input_items)
        content = ItemHelpers.text_message_outputs(content_result.new_items)

        evaluation_input = [{"content": f"{prompt}\n\nGenerated: {content}", "role": "user"}]
        eval_result = await Runner.run(evaluator_agent, evaluation_input)
        feedback = eval_result.final_output

        print(f"Score: {feedback.score}\nFeedback: {feedback.feedback}")

    with trace("Store content"):
        store_result = await Runner.run(storage_agent, [{"content": content, "role": "user"}])

    with trace("Schedule post"):
        await Runner.run(scheduler_agent, [{"content": str(store_result), "role": "user"}])

if __name__ == "__main__":
    asyncio.run(main())
