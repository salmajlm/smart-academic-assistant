# Smart Academic Assistant (ENSAke-website & Gmail Automation)

## Description

Smart Academic Assistant is a Python-based automation system designed to help students manage academic information more efficiently.
It collects emails from Gmail and announcements from the ENSA website, processes the data, analyzes it using a language model, and generates a structured daily summary.

The final output is a concise message intended for quick reading on mobile (e.g., WhatsApp).

---

## Features

- Gmail integration using OAuth 2.0
- Web scraping of ENSA announcements
- Data preprocessing and normalization
- Automatic classification of emails (urgency, deadline, required action)
- AI-based content analysis using LLMs
- Merging of multiple information sources
- Generation of a structured daily summary

---

## Project Structure
auto_email_workflow.py # Main pipeline controller
gmail_collector.py # Gmail API integration
scraper_ensa.py # Website scraping module
preprocessor.py # Data cleaning utilities
ai_analyzer.py # Email analysis using LLM
summary_agent.py # Final message generation
notifier.py # WhatsApp notification sender


---

## Technologies Used

- Python 3.10+
- LangChain
- OpenAI / Ollama (LLMs)
- Gmail API (OAuth 2.0)
- BeautifulSoup
- Pydantic
- Twilio API

---

## Installation

### 1. Clone repository

git clone https://github.com/your-username/smart-academic-assistant.git
cd smart-academic-assistant

2. Install dependencies
pip install -r requirements.txt
3. Environment variables

Create a .env file:

OPENAI_API_KEY=your_api_key
AI_PROVIDER=openai

TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+141xxxxxxxx
USER_WHATSAPP_TO=whatsapp:+212XXXXXXXXX
4. Google API setup

Add the file:

credentials.json

(Generated from Google Cloud Console)

Usage :

Run full workflow
python auto_email_workflow.py

Test mode (without sending messages)
python main.py

Security Notes:

The following files must NOT be shared or pushed to GitHub:

.env
token.json
credentials.json

Make sure they are included in .gitignore.

System Overview:
Emails are retrieved from Gmail API
ENSA announcements are scraped from the official website
Data is cleaned and standardized
An AI model analyzes and classifies each item
Information is merged into a single structured summary
The final message is sent via WhatsApp
