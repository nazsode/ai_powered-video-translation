import streamlit as st
import ffmpeg
import os
from tempfile import NamedTemporaryFile
import whisper
from mtranslate import translate
from moviepy.editor import VideoFileClip, AudioFileClip
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup

# Define some custom CSS for styling
st.markdown("""
    <style>
    .title {
        font-size: 36px;
        color: #4CAF50;
        text-align: center;
    }
    .subtitle {
        font-size: 24px;
        color: #2196F3;
    }
    .container {
        background-color: #f4f4f4;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
        margin: 10px 0;
    }
    .button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("<h1 class='title'>AI Destekli Video Çeviri Uygulaması</h1>", unsafe_allow_html=True)

# Seçimlerin ve çevirilerin saklanacağı alan
if 'selected_languages' not in st.session_state:
    st.session_state.selected_languages = []
if 'translations' not in st.session_state:
    st.session_state.translations = {}

# Video dosyası yükleme
st.sidebar.header("Video Yükleme ve Dil Seçimi")
uploaded_video = st.sidebar.file_uploader("Bir video dosyası yükleyin", type=["mp4", "avi", "mov"])

# Çeviri dillerini seçme
languages = ['tr', 'fr', 'de', 'en']  # Türkçe, Fransızca, Almanca, İngilizce
language_names = ['Türkçe', 'Fransızca', 'Almanca', 'İngilizce']

st.sidebar.write("Çevirmek istediğiniz dilleri seçin:")
for language_name in language_names:
    if st.sidebar.checkbox(language_name, key=language_name):
        if language_name not in st.session_state.selected_languages:
            st.session_state.selected_languages.append(language_name)
    else:
        if language_name in st.session_state.selected_languages:
            st.session_state.selected_languages.remove(language_name)

# Seçilen dillerin kodlarını döndüren yardımcı fonksiyon
def get_language_code(language_name):
    language_mapping = dict(zip(language_names, languages))
    return language_mapping.get(language_name)

def video_to_audio(input_video):
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(input_video.read())
        temp_video_path = temp_video.name

    audio_output = temp_video_path.replace(".mp4", ".mp3")

    # ffmpeg komutu ile videoyu sese dönüştürme
    ffmpeg.input(temp_video_path).output(audio_output).run()

    return audio_output

def transcribe_audio_locally(audio_file_path):
    # Whisper modelini yerel olarak yükle
    model = whisper.load_model("base")

    # Ses dosyasını metne çevir
    result = model.transcribe(audio_file_path)

    return result["text"]

def translate_text(text, target_language_code):
    # Yerel çeviri kütüphanesi ile metni çevirmek
    return translate(text, target_language_code)

def text_to_audio(text, language_code):
    # Google Text-to-Speech kullanarak metni ses dosyasına dönüştür
    tts = gTTS(text=text, lang=language_code)
    audio_path = f"translation_{language_code}.mp3"
    tts.save(audio_path)
    return audio_path

# Ses dosyalarını hızlılaştırma fonksiyonu
def speed_up_audio(audio_path):
    audio_segment = AudioSegment.from_mp3(audio_path)
    faster_audio_segment = speedup(audio_segment, playback_speed=1.0)
    faster_audio_path = f"faster_{os.path.basename(audio_path)}"
    faster_audio_segment.export(faster_audio_path, format="mp3")
    return faster_audio_path

# Eğer video yüklendiyse ve diller seçildiyse
if uploaded_video is not None and st.session_state.selected_languages:
    st.write("Video dosyası başarıyla yüklendi.")
    st.write(f"Seçilen diller: {', '.join(st.session_state.selected_languages)}")

    # İşlemi başlatmak için bir buton
    if st.button("Çeviriyi Başlat", key="start_button", help="Video işleme ve çeviri işlemlerini başlatır."):
        st.write("Video işleniyor...")

        # Videoyu sese dönüştürme işlemi
        audio_file = video_to_audio(uploaded_video)
        st.write("Ses dosyası oluşturuldu:", audio_file)

        # Ses dosyasını Whisper ile metne çevir
        transcription = transcribe_audio_locally(audio_file)
        st.write("Transkript oluşturuldu:")
        st.text_area("Transkript:", transcription, height=200)

        # Seçilen dillerde çevirileri yapma
        st.session_state.translations = {}
        for language_name in st.session_state.selected_languages:
            language_code = get_language_code(language_name)
            st.session_state.translations[language_code] = translate_text(transcription, language_code)
            st.write(f"{language_name} diline çevrildi:")
            st.text_area(f"{language_name} Çevirisi:", st.session_state.translations[language_code], height=150)

        # Video dosyasını geçici olarak sakla
        with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_path = temp_video_file.name
            uploaded_video.seek(0)
            temp_video_file.write(uploaded_video.read())

        # Her dil için ayrı video oluşturma
        for language_name in st.session_state.selected_languages:
            language_code = get_language_code(language_name)
            translation = st.session_state.translations[language_code]
            audio_path = text_to_audio(translation, language_code)
            faster_audio_path = speed_up_audio(audio_path)

            # Final ses dosyasını videoya ekleme
            video = VideoFileClip(temp_video_path)
            audio = AudioFileClip(faster_audio_path)
            final_video = video.set_audio(audio)
            final_video_path = f"final_video_{language_name}.mp4"
            final_video.write_videofile(final_video_path, codec='libx264')

            st.write(f"{language_name} dilinde video oluşturuldu.")

            # Her dil için çeviriyi indirilebilir hale getirme
            file_name = f"transcription_{language_name}.txt"
            with open(file_name, "w") as file:
                file.write(translation)

            with open(file_name, "rb") as file:
                st.download_button(
                    label=f"{language_name} çevirisini indir",
                    data=file,
                    file_name=file_name,
                    mime="text/plain",
                    key=f"download_transcription_{language_name}"
                )

            # Her dil için final videoyu indirilebilir hale getirme
            with open(final_video_path, "rb") as file:
                st.download_button(
                    label=f"{language_name} videoyu indir",
                    data=file,
                    file_name=final_video_path,
                    mime="video/mp4",
                    key=f"download_video_{language_name}"
                )

else:
    st.warning("Lütfen bir video yükleyin ve çevirmek istediğiniz dilleri seçin.")
