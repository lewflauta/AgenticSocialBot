# AgenticSocialBot

Here's your explanation adapted for a clean and professional **GitHub README.md** file format:

---

# 🧠 Multi-Agent Social Media Automation Bot

Automatically generate, critique, store, and schedule social media posts from YouTube videos using OpenAI and Google APIs.

## 🚀 Project Overview

This project is a fully asynchronous, multi-agent automation system that converts a YouTube transcript into polished, platform-optimized social media content. It includes quality evaluation, cloud storage via Google Drive, and auto-scheduling with Google Calendar.

---

## ⚙️ Features

* 🔍 Extracts transcripts from YouTube videos
* ✍️ Generates high-quality social media content using GPT-4o
* 🧠 Critiques and scores the content with actionable feedback
* ☁️ Stores the content to Google Drive as `.txt` files
* 📅 Schedules the post in Google Calendar for optimal timing

---

## 🧰 Tech Stack

| Tool / Service       | Purpose                         |
| -------------------- | ------------------------------- |
| Python 3.11+         | Core programming language       |
| OpenAI GPT-4o        | Content generation and critique |
| YouTubeTranscriptAPI | Transcript extraction           |
| Google Drive API     | File storage                    |
| Google Calendar API  | Post scheduling                 |
| dotenv               | Environment variable management |
| asyncio              | Asynchronous task handling      |

---

## 🧩 System Architecture

```
YouTube Video → Transcript → Content Writer Agent
                          ↓
                   Critic Agent → Feedback Loop
                          ↓
                 Storage Agent → Google Drive
                          ↓
             Scheduler Agent → Google Calendar
```

---

## 🔄 Execution Flow

```python
async def main():
    transcript = fetch_transcript(video_id)
    content = writer_agent(transcript)
    feedback = evaluator_agent(content)
    save_post_to_drive(content)
    schedule_post_on_calendar(content_link)
```

Run with:

```bash
python main.py
```

---

## 📂 Folder & File Structure

```
.
├── main.py                # Orchestrates the agent flow
├── agents.py              # Custom agent & runner logic
├── .env                   # Stores API keys securely
├── social-media-agent.json # Google API service credentials
└── README.md              # Project documentation
```

---

## 🔑 Setup & Configuration

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Add your environment variables**

```
OPENAI_API_KEY=your_openai_key_here
```

3. **Add your Google Service Account JSON**

* Enable Google Drive and Calendar APIs
* Save the credentials as `social-media-agent.json`

---

## 📌 Future Enhancements

* Add image generation for visual posts
* Support for Twitter/X and Facebook
* UI for uploading video links and managing posts
* Multi-language support


