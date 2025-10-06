# customer_support_chatbot
# Customer Support Chatbot – Euron AI

A voice-enabled, document-aware customer support chatbot built with **Streamlit**, **LangChain**, **Google Generative AI**, and **ElevenLabs TTS**. It allows users to ask questions about products, services, and policies via text or voice and dynamically updates its knowledge base from uploaded documents.

---

## Features

- Conversational AI powered by Google Gemini LLM
- Voice input (Whisper) and output (ElevenLabs TTS)
- Upload documents (PDF, TXT, MD, HTML) to update knowledge
- Multilingual support via GoogleTranslator
- Interactive Streamlit UI with chat history management

---

## Project Structure

customer_support_chatbot/
│
├─ app.py # Main Streamlit application
├─ utils.py # Helper functions: TTS, transcription, document extraction, AI response
├─ uploads/ # Folder for user-uploaded files
├─ vectorstore/ # FAISS vectorstore storage
├─ company_docs.txt # Base knowledge document
├─ .env # API keys (ELEVENLABS_API_KEY, etc.)
└─ README.md
## Installation & Setup

1. **Clone the repository**
```
git clone https://github.com/arpit000000/customer_support_chatbot.git
cd customer_support_chatbot
Activate your virtual environment (lang6)

Windows:



C:\pwML\objectDetection\FaceRecogAcademy\lang6\Scripts\activate
Mac/Linux:



source /path/to/lang6/bin/activate
Install dependencies



pip install -r requirements.txt
Set up .env file with your API key:


ELEVENLABS_API_KEY=your_elevenlabs_api_key
Running the App


streamlit run app.py
Open the provided URL (usually http://localhost:8501) in your browser.

Type or speak your questions, upload documents, and interact with the chatbot.

Notes / Troubleshooting
ElevenLabs TTS requires a valid voice name. List available voices:

python

from elevenlabs import ElevenLabs
import os

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
voices = client.voices.get_all()
for v in voices.voices:
    print(v.name)
Ensure your microphone works for voice input (Whisper + sounddevice).

LangChain may show Chain.__call__ deprecation warnings — they can be ignored or updated to .invoke().
## Author

Arpit Jadon
