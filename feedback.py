import streamlit as st
import openai
import os

# Streamlit App Title
st.title("Interview Feedback Chatbot")

# Sidebar for OpenAI API Key Input
st.sidebar.header("Settings")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Initialize OpenAI API Key
if openai_api_key:
    openai.api_key = openai_api_key
else:
    st.warning("Please enter your OpenAI API key in the sidebar to proceed.")

# Function to Transcribe Audio using OpenAI Whisper
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio:
        transcript = openai.Audio.transcribe("whisper-1", audio)
    return transcript['text']

# Function to Analyze Text and Provide Feedback
def analyze_text(user_input):
    prompt = f"""
    You are an expert interviewer and conversation analyst. Provide conversational feedback on the following:
    - Did the person communicate clearly?
    - Does the job sound like a good “fit” for them?
    - Did they hit their goals for the interview? If not, what was missed?
    - What question surprised them?
    - One thing they could have done differently to improve.
    - Were their questions thoughtful and well-received?
    - Did anything feel off or strange (like a "spider sense" moment)?

    Here's the text for analysis:
    {user_input}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful and thoughtful interview feedback chatbot."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response['choices'][0]['message']['content']

# Upload Audio for Transcription (Optional)
st.subheader("Upload an Interview Audio File (Optional)")
uploaded_audio = st.file_uploader("Upload your audio file (mp3, wav, etc.)", type=["mp3", "wav", "ogg"])

# Audio Transcription Section
if uploaded_audio and openai_api_key:
    try:
        # Save uploaded audio to disk
        audio_file_path = "uploaded_audio.mp3"
        with open(audio_file_path, "wb") as f:
            f.write(uploaded_audio.read())

        # Transcribe audio
        st.info("Transcribing audio...")
        transcribed_text = transcribe_audio(audio_file_path)
        st.success("Transcription completed!")
        st.text_area("Transcribed Interview Text", transcribed_text, height=200)

        # Cleanup audio file
        os.remove(audio_file_path)

    except Exception as e:
        st.error(f"An error occurred while transcribing audio: {e}")

# Chatbot Section
st.subheader("Chat with the Interview Feedback Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.text_input("You", value=message["content"], key=message["content"], disabled=True)
    else:
        st.text_area("Bot", value=message["content"], key=message["content"], height=150, disabled=True)

# User input field
user_input = st.text_input("Your Message:", key="user_input")
if user_input and openai_api_key:
    try:
        # Add user input to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate feedback from GPT-4
        with st.spinner("Thinking..."):
            bot_response = analyze_text(user_input)
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        # Display bot response
        st.text_area("Bot", value=bot_response, height=150, disabled=True)

    except Exception as e:
        st.error(f"An error occurred while generating feedback: {e}")
