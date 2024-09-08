autocompletion_prompt = """
You are a helpful assistant. Based on the user's prompt and the context provided, suggest an autocomplete response that is in the user's voice and relevant to their current needs. Do not include any assistant messages or explanations—just the response. 

Context: {context}

Prompt: {prompt}

Response:
"""

generalist_prompt = """
**Task:**
Analyze the content displayed on the screen and output structured data based on what is visible. The content could include a calendar, a dialogue (chat), or tabular data. For each type of content, transcribe the relevant information into a structured JSON format.

**Instructions:**

1. **Calendar:**
   - If a calendar is visible, log all events with their:
     - Date
     - Start time
     - End time
     - Event description or title
   - Format the information into JSON.

2. **Dialogue (Text space):**
   - If a chat interface is visible (e.g., Slack, messaging app), capture the details of the conversation, including:
     - Sender(s)
     - Recipient(s)
     - Timestamp of each message (if available)
     - Message content
   - Format the chat history into JSON.

3. **Tabular Data:**
   - If there is a table visible, extract all the data, including headers and corresponding values in rows.
   - Format this tabular data into JSON.

**Expected Output:**
For each section, output a JSON object with the following structure:

```json
{
  "source": "string",  # Application or website from which the data is being extracted
  "summary": "string",  # A brief description of the content (e.g., 'Calendar events for the week', 'Chat conversation', 'Table of sales data')
  "details": "string"  # Log the extracted data in detail. For calendars, this includes events, dates, and times. For dialogues, this includes chat participants and message history. For tables, this includes headers and corresponding data.
}
```

**Examples:**

1. **Calendar Example:**

```json
{
  "source": "Google Calendar",
  "summary": "Calendar events for the week",
  "details": "Event 1: Meeting with John | Date: 2024-09-10 | Start: 10:00 AM | End: 11:00 AM\nEvent 2: Project Deadline | Date: 2024-09-12 | Start: 5:00 PM | End: 6:00 PM"
}
```

2. **Dialogue Example:**

```json
{
  "source": "Slack - #project-channel",
  "summary": "Conversation log",
  "details": "John: 'Can we move the meeting to Friday?' | Time: 9:45 AM\nSarah: 'Friday works for me' | Time: 9:47 AM"
}
```

3. **Tabular Data Example:**

```json
{
  "source": "Excel Spreadsheet - Sales Report",
  "summary": "Sales data table",
  "details": "Header: 'Product', 'Sales', 'Revenue'\nRow 1: 'Widget A', '100', '$5000'\nRow 2: 'Widget B', '200', '$10000'"
}
```
"""

conversation_prompt = """
**Task:**
Analyze a UI screenshot of a chat interface and extract the main conversation in focus. Ignore side conversations or threads and concentrate solely on the primary dialogue.

**Instructions:**

1. **Main Conversation:**
   - Identify the person or group we are corresponding with in the main chat window.
   - Extract all messages from the conversation, including:
     - Sender
     - Message content
   - Ignore any sidebars or secondary threads.
   
2. **Format the conversation data into JSON:**
   - Use the provided JSON structure to organize the data.
   - Each message in the conversation should have the sender and message logged.

**Expected Output:**
The conversation should be formatted as follows using the classes `ChatMessage` and `Conversation`:

```json
{
  "person_we_are_corresponding_to": "string",  # Name of the person or group in the main chat
  "messages": [
    {
      "sender": "string",  # The name or ID of the person who sent the message
      "message": "string"  # The actual message content
    },
    {
      "sender": "string",
      "message": "string"
    }
  ]
}
```

**Examples:**

1. **Slack Conversation Example:**

```json
{
  "person_we_are_corresponding_to": "John Doe",
  "messages": [
    {
      "sender": "John Doe",
      "message": "Hey, can you share the report?"
    },
    {
      "sender": "Me",
      "message": "Sure, I'll send it in a few minutes."
    }
  ]
}
```

2. **Messaging App Example:**

```json
{
  "person_we_are_corresponding_to": "Project Team",
  "messages": [
    {
      "sender": "Alice",
      "message": "The deadline is approaching. Any updates?"
    },
    {
      "sender": "Me",
      "message": "We're nearly done, just finalizing a few things."
    },
    {
      "sender": "Bob",
      "message": "I'll help with the final review."
    }
  ]
}
```
"""