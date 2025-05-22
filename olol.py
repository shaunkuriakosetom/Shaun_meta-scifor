# Step 1: Install required packages
!pip install gTTS IPython

# Step 2: Import libraries
from gtts import gTTS
from IPython.display import Audio, display
import uuid
import os

# Step 3: Take text input
text = input("📝 Enter the text to convert to speech:\n")

if text.strip():
    filename = f"{uuid.uuid4()}.mp3"
    
    # Step 4: Generate speech
    tts = gTTS(text)
    tts.save(filename)

    # Step 5: Play audio
    print("🔊 Playing audio...")
    display(Audio(filename, autoplay=True))
    
    # Optional: Enable download link
    from google.colab import files
    files.download(filename)
else:
    print("⚠️ Please enter valid text.")
