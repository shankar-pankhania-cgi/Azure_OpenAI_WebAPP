import streamlit as st
from azureopenai_pdf_vectored import process_message 
from dotenv import load_dotenv
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
        # if model_type == "Use base GPT-4 model":
        #     for response in create_chat_completion(deployment_name, st.session_state.messages, aoai_endpoint, aoai_key):
        #         if response.choices:
        #             full_response += (response.choices[0].delta.content or "")
        #             message_placeholder.markdown(full_response + "▌")
        # else:
        #     for response in create_chat_with_data_completion(deployment_name, st.session_state.messages, aoai_endpoint, aoai_key, search_endpoint, search_key, search_index_name):
        #         if response.choices:
        #             full_response += (response.choices[0].delta.content or "")
        #             message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
 
def main():
    st.write(
    """
    # Chat with Data

    This Streamlit dashboard is intended to show off capabilities of Azure OpenAI, including integration with AI Search, Azure Speech Services, and external APIs.
    """
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []


    aoai_endpoint = st.secrets["aoai"]["AZURE_OPENAI_ENDPOINT"]
    aoai_key = st.secrets["aoai"]["AZURE_OPENAI_API_KEY"]
    aoai_deployment_name = st.secrets["aoai"]["AZURE_OPENAI_DEPLOYMENT_NAME"]

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