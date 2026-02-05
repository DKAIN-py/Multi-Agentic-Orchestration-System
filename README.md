# Communication Agent (WIP)

A local CrewAI project designed to automate fetching contact details from CSVs and sending messages via Email (SMTP) or WhatsApp (Twilio) based on natural language prompts.

**Status:** In Development 🚧

## 🔄 Workflow

1. **Info Extractor:** Parses the input to find names, lists, or groups (e.g., "All Clients"), and determines the medium (Email/WhatsApp).
2. **Contact Lookup:** Searches `client.csv` or `employee.csv` to find emails and phone numbers.
3. **Content Generator:** Drafts the message body based on the requested tone.
4. **Sender:** Iterates through the list of recipients and executes the sending tool (Gmail or Twilio).

## 📂 Project Structure

* `src/CommunicationAgent/`
  * `main.py`: Entry point. Define `inputs={'input_text': '...'}` here.
  * `crew.py`: Agent and Task definitions.
  * `tools.py`: Custom logic for CSV search, Gmail, and Twilio.
  * `models.py`: Pydantic schemas for structured output.
* `client.csv` / `employee.csv`: Local databases.

## 🛠️ Setup

1. **Install Dependencies:**
   ```bash
   pip uv
   uv sync

2. **Environment Variables (.env): Create a .env file in the root**
    ```bash
    MODEL=sk-...
    MODEL_NAME=gemini-2.5-flash

    # Tools
    MY_EMAIL=...
    MY_APP_PASSWORD=...
    TWILIO_SID=...
    TWILIO_TOKEN=...

3. **Run**
    ```bash
    uv communicationagent/src/communicationagent/main.py

# Notes
- CSV Search: Matches full_name in client.csv and name in employee.csv
- Batching: Supports "ALL_CLIENTS" and "ALL_EMPLOYEES" keywords to fetch the entire list
- WhatsApp: Currently runs in Sandbox mode; ensure recipient numbers are verified in Twilio console.