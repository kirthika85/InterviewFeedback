import streamlit as st
import openai
import os

# Streamlit App Title
st.title("Interview Feedback Generator")

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
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )
    return response.text

# Function to Analyze Text and Provide Feedback
def analyze_text(interview_text):
    prompt = f"""
    You are an expert interviewer and conversation analyst. Provide insightful feedback based on the interview text. Cover the following:
    - Did the person communicate clearly?
    - Does the job sound like a good “fit” for them?
    - Did they hit all their goals for the interview? If not, what did they miss?
    - What question surprised them?
    - What’s one thing they could have done differently to improve their interview?
    - Were their questions thoughtful and well-received?
    - Did anything feel slightly off, like a "spider sense" moment, where something didn't seem right?

    Interview Text:
    {interview_text}
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert at analyzing interviews and providing thoughtful feedback."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

# Function to check if the text seems to be an interview
def is_interview(text):
    # Define keywords that are common in interviews
    interview_keywords = ["interview", "job", "role", "position", "hiring", "candidate", "interviewed"]
    text_lower = text.lower()

    # Check if any of the keywords are found in the transcribed text
    for keyword in interview_keywords:
        if keyword in text_lower:
            return True
    return False

# Upload Audio File
st.subheader("Upload an Interview Audio File")
uploaded_audio = st.file_uploader("Upload your audio file (mp3, wav, etc.)", type=["mp3", "wav", "ogg"])

# Main Logic for Transcription and Feedback
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

        # Check if the transcription is about an interview
        if is_interview(transcribed_text):
            # Display Transcribed Text
            st.subheader("Transcribed Interview Text")
            st.text_area("Transcription", transcribed_text, height=200)

            # Analyze Transcription and Provide Feedback
            st.info("Generating feedback based on the interview text...")
            feedback = analyze_text(transcribed_text)
            st.success("Feedback generated!")

            # Display Feedback
            st.subheader("Interview Feedback")
            st.write(feedback)

        else:
            st.warning("The uploaded audio doesn't seem to be an interview. Please upload a relevant interview file.")

        # Cleanup audio file
        os.remove(audio_file_path)

    except Exception as e:
        st.error(f"An error occurred: {e}")

elif not openai_api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to proceed.")

else:
    st.info("Upload an audio file to get started.")
