import streamlit as st
from azureopenai_pdf_vectored import process_message 
from dotenv import load_dotenv#

load_dotenv()


def handle_chat_prompt(prompt, deployment_name, aoai_endpoint, aoai_key):
    # Echo the user's prompt to the chat window
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the user's prompt to Azure OpenAI and display the response
    # The call to Azure OpenAI is handled in create_chat_completion()
    # This function loops through the responses and displays them as they come in.
    # It also appends the full response to the chat history.
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = process_message(prompt)
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
 
def main():
    st.title("United Kingdom History Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Gets Azure credentials using streamlit secrets
    aoai_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
    aoai_key = st.secrets["AZURE_OPENAI_API_KEY"]
    aoai_deployment_name = st.secrets["AZURE_OPENAI_DEPLOYMENT_NAME"]

     # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if ('transcription_results' in st.session_state):
        speech_contents = ' '.join(st.session_state.transcription_results)
        del st.session_state.transcription_results
        handle_chat_prompt(speech_contents, aoai_deployment_name, aoai_endpoint, aoai_key)

    # Await a user message and handle the chat prompt when it comes in.
    if prompt := st.chat_input("Enter a message:"):
        handle_chat_prompt(prompt, aoai_deployment_name, aoai_endpoint, aoai_key)

if __name__ == "__main__":
    main()