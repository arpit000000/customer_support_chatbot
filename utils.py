
# import os
# import tempfile
# import streamlit as st
# from dotenv import load_dotenv
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.vectorstores import FAISS
# from langchain.chains import ConversationalRetrievalChain
# from langchain.text_splitter import CharacterTextSplitter

# from elevenlabs.client import ElevenLabs
# import fitz
# from deep_translator import GoogleTranslator
# import whisper
# import sounddevice as sd
# from scipy.io.wavfile import write


# load_dotenv()
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")



# VECTOR_STORE_DIR = "vectorstore"
# DOC_FILE = "company_docs.txt"
# VECTOR_STORE_PATH = os.path.join(VECTOR_STORE_DIR, "company_vectorstore")


# def load_vectorstore():
#     if st.session_state.vectorstore is not None:
#         return st.session_state.vectorstore

#     embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

#     if os.path.exists(VECTOR_STORE_PATH) and not st.session_state.knowledge_updated:
#         try:
#             vectorstore = FAISS.load_local(
#                 VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
#             )
#             st.session_state.vectorstore = vectorstore
#             return vectorstore
#         except Exception as e:
#             st.error(f"Error loading vectorstore: {str(e)}")



#     try:
#         with open(DOC_FILE, "r", encoding="utf-8") as f:
#             text = f.read()

#         for file_info in st.session_state.uploaded_files:
#             text += f"\n\n{file_info['content']}"

#         text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         docs = text_splitter.split_text(text)

#         vectorstore = FAISS.from_texts(docs, embeddings)
#         vectorstore.save_local(VECTOR_STORE_PATH)

#         st.session_state.vectorstore = vectorstore
#         st.session_state.knowledge_updated = False
#         return vectorstore
#     except Exception as e:
#         st.error(f"Error creating vectorstore: {str(e)}")
#         return None


# def whisper_transcribe(duration=5, samplerate=16000):
#     audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
#     sd.wait()
#     temp_audio_file = tempfile.mktemp(suffix=".wav")
#     write(temp_audio_file, samplerate, audio)

#     model = whisper.load_model("base")
#     result = model.transcribe(temp_audio_file)

#     os.remove(temp_audio_file)
#     return result["text"]


# def elevenlabs_tts(text, lang="en", voice="Rachel"):
#     client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
#     audio = client.generate(
#         text=text,
#         voice=voice,
#         model="eleven_multilingual_v2" if lang != "en" else "eleven_monolingual_v1"
#     )
#     temp_audio_file = tempfile.mktemp(suffix=".mp3")
#     with open(temp_audio_file, "wb") as f:
#         for chunk in audio:
#             f.write(chunk)
#     return temp_audio_file


# def extract_text_from_file(uploaded_file):
#     file_content = uploaded_file.getvalue()
#     file_extension = uploaded_file.name.split(".")[-1].lower()


#     if file_extension == "pdf":
#         try:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
#                 tmp_file.write(file_content)
#                 tmp_file_path = tmp_file.name

#             doc = fitz.open(tmp_file_path)
#             text = "".join(page.get_text() for page in doc)

#             os.unlink(tmp_file_path)
#             return text
#         except Exception as e:
#             st.error(f"Error extracting text from PDF: {str(e)}")
#             return ""
#     elif file_extension in ["txt", "md", "html"]:
#         return file_content.decode("utf-8")
#     else:
#         st.warning(f"Unsupported file type: {file_extension}")
#         return ""
    


# def get_ai_response(query, lang="en"):
#     vectorstore = load_vectorstore()
#     if not vectorstore:
#         return "Error loading knowledge base. Please try again.", []

#     query_en = GoogleTranslator(source=lang, target='en').translate(query) if lang != "en" else query

#     try:
#         llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
#         qa_chain = ConversationalRetrievalChain.from_llm(
#             llm=llm, retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), return_source_documents=True
#         )

#         result = qa_chain({"question": query_en, "chat_history": st.session_state.conversation_history})

#         answer_en = result["answer"]
#         sources = [doc.page_content[:150] + "..." for doc in result.get("source_documents", [])]

#         answer = GoogleTranslator(source='en', target=lang).translate(answer_en) if lang != "en" else answer_en

#         st.session_state.conversation_history.append((query_en, answer_en))

#         return answer, sources
#     except Exception as e:
#         return f"Error generating response: {str(e)}", []

import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter

from elevenlabs.client import ElevenLabs
import fitz
from deep_translator import GoogleTranslator
from scipy.io.wavfile import write
import whisper
import sounddevice as sd
import numpy as np

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

VECTOR_STORE_DIR = "vectorstore"
DOC_FILE = "company_docs.txt"
VECTOR_STORE_PATH = os.path.join(VECTOR_STORE_DIR, "company_vectorstore")


def load_vectorstore():
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    # Agar vectorstore exist karta hai aur knowledge updated nahi hai
    if os.path.exists(VECTOR_STORE_PATH) and not st.session_state.get("knowledge_updated", True):
        try:
            vectorstore = FAISS.load_local(
                VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
            )
            st.session_state.vectorstore = vectorstore
            return vectorstore
        except Exception as e:
            st.error(f"Error loading vectorstore: {str(e)}")

    # Merge DOC_FILE + uploaded files
    try:
        text = ""
        if os.path.exists(DOC_FILE):
            with open(DOC_FILE, "r", encoding="utf-8") as f:
                text = f.read()

        for file_info in st.session_state.get("uploaded_files", []):
            text += f"\n\n{file_info['content']}"

        if not text.strip():
            st.warning("No documents found to build vectorstore.")
            return None

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_text(text)

        vectorstore = FAISS.from_texts(docs, embeddings)
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
        vectorstore.save_local(VECTOR_STORE_PATH)

        st.session_state.vectorstore = vectorstore
        st.session_state.knowledge_updated = False
        return vectorstore

    except Exception as e:
        st.error(f"Error creating vectorstore: {str(e)}")
        return None




def whisper_transcribe(duration=5, samplerate=16000):
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    audio = np.squeeze(audio)
    temp_audio_file = os.path.join("uploads", f"recording_{int(np.random.rand()*1e6)}.wav")
    write(temp_audio_file, samplerate, audio)
    model = whisper.load_model("base")
    result = model.transcribe(audio, fp16=False)  # Pass raw audio
    return result["text"]




def elevenlabs_tts(text, lang="en", voice="Rachel"):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.generate(
        text=text,
        voice=voice,
        model="eleven_multilingual_v2" if lang != "en" else "eleven_monolingual_v1"
    )
    temp_audio_file = tempfile.mktemp(suffix=".mp3")
    with open(temp_audio_file, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return temp_audio_file



def extract_text_from_file(uploaded_file):
    os.makedirs("uploads", exist_ok=True)  # Ensure uploads folder exists
    file_path = os.path.join("uploads", uploaded_file.name)
    
    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
        
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "pdf":
        try:
            import fitz
            doc = fitz.open(file_path)  # open saved file directly
            text = "".join(page.get_text() for page in doc)
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    elif file_extension in ["txt", "md", "html"]:
        return uploaded_file.getvalue().decode("utf-8")
    else:
        st.warning(f"Unsupported file type: {file_extension}")
        return ""


def get_ai_response(query, lang="en"):
    vectorstore = load_vectorstore()
    if not vectorstore:
        return "Error loading knowledge base. Please try again.", []

    query_en = GoogleTranslator(source=lang, target='en').translate(query) if lang != "en" else query

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm, retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), return_source_documents=True
        )

        result = qa_chain({"question": query_en, "chat_history": st.session_state.get("conversation_history", [])})

        answer_en = result["answer"]
        sources = [doc.page_content[:150] + "..." for doc in result.get("source_documents", [])]

        answer = GoogleTranslator(source='en', target=lang).translate(answer_en) if lang != "en" else answer_en

        st.session_state.conversation_history.append((query_en, answer_en))

        return answer, sources
    except Exception as e:
        return f"Error generating response: {str(e)}", []
