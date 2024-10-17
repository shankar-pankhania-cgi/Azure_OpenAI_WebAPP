import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from openai.types import FileObject

load_dotenv()

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-05-01-preview",
)


def upload_file(client: AzureOpenAI, path: str) -> FileObject:
    with Path(path).open("rb") as file:
        return client.files.create(file=file, purpose="assistants")
    
dir = "Data/"
files = os.listdir(dir)
assistant_files = []
for file in files:
    filePath = dir + file
    assistant_files.append(upload_file(client, filePath))

file_ids = [file.id for file in assistant_files]

# Create an assistant
assistant = client.beta.assistants.create(
    name="History Analyst Assistant",
    instructions="You are an expert history analyst. Use your knowledge base to answer questions about the history of United Kingdom.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
    tool_resources={"code_interpreter": {"file_ids": file_ids}}
)

# Create a thread
thread = client.beta.threads.create()


def process_message(content: str):
    # Add a user question to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
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
