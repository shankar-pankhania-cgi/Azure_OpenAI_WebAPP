import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from openai.types import FileObject
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-05-01-preview",
)

def upload_file(client: AzureOpenAI, path: str) -> FileObject:
    with Path(path).open("rb") as file:
        return client.files.create(file=file, purpose="assistants")

file_paths = ["Data/united_kingdom.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

# Create an assistant
assistant = client.beta.assistants.create(
  name="History Analyst Assistant",
  instructions="You are an expert history analyst. Use your knowledge base to answer questions about the history of United Kingdom.",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
)

# Create a vector store called "United Kingdom History"
vector_store = client.beta.vector_stores.create(
  name="United Kingdom History",
  expires_after={
  "anchor": "last_active_at",
  "days": 1
  }
)
 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(vector_store_id=vector_store.id, files=file_streams)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Upload the user provided file to OpenAI
message_file = upload_file(client, "Data/united_kingdom.pdf")
 
def process_message(content: str):
    thread = client.beta.threads.create(
      messages=[
        {
          "role": "user",
          "content": content,
          "attachments": [
            { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
          ],
        }
      ]
    )

    # Run the thread for the result
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            messages = messages.to_json(indent=2)
            messages = json.loads(messages)
            break
        else:
             time.sleep(5)

    contents = []
    for message in messages["data"]:
        if 'content' in message:
            for content_item in message['content']:
                if 'text' in content_item and 'value' in content_item['text']:
                    contents.append(content_item['text']['value'])

    return contents[0]