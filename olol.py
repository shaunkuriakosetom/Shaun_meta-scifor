
!pip install gTTS IPython

from gtts import gTTS
from IPython.display import Audio, display
import uuid
import os

text = input("📝 Enter the text to convert to speech:\n")

if text.strip():
    filename = f"{uuid.uuid4()}.mp3"

    tts = gTTS(text)
    tts.save(filename)

    print("🔊 Playing audio...")
    display(Audio(filename, autoplay=True))

    from google.colab import files
    files.download(filename)
else:
    print("⚠️ Please enter valid text.")
