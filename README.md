#AI-Powered Video Translation Application
This project is a Streamlit application that allows users to upload videos, select target languages, and get translations in those languages. The application converts the video to audio, transcribes the audio to text, translates the text into selected languages, and then combines the translations with the original video.

**Features**
-Upload video files and select target languages for translation.
-Convert video to audio and transcribe the audio to text.
-Translate the text into selected languages and combine translations with the video.
-Make translations and final videos available for download.

**Requirements**
-Python 3.8 or higher
-Streamlit
-ffmpeg-python
-whisper
-mtranslate
-moviepy
-gTTS
-pydub

To install the required packages:
```bash
pip install streamlit ffmpeg-python whisper mtranslate moviepy gtts pydub
```

**Usage**
Run the Application: Open a terminal, navigate to the directory containing app.py, and run:
```bash
streamlit run app.py
```

Upload Video: Use the sidebar to upload a video file (.mp4, .avi, or .mov format).

Select Languages: Choose the languages you want to translate the video into. Supported languages: Turkish, French, German, English.

Start Translation: Click the Start Translation button to begin the video processing and translation.

Results: Once the process is complete, the translations and final video will be available for download.

**Contributing**
If you wish to contribute, please submit a pull request or check out the issue tracker.

**License**
This project is licensed under the MIT License.
