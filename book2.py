import streamlit as st
import requests
import PyPDF2

# ========================== #
# 🔐 Set Your Keys in Code
# ========================== #
GEMINI_API_KEY = "AIzaSyC_-yOtyWqcCFaTumMy0zdJm5WeGkGGqk8"  # Replace with your Gemini 2.0 Flash API key
WEBHOOK_URL = "https://navin22.app.n8n.cloud/webhook-test/Response"  # Replace with your webhook URL (optional)
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# ========================== #
# 📚 Streamlit UI Setup
# ========================== #
st.set_page_config(page_title="📖 Book Summary App", layout="centered")
st.title("📚 Book Summary App (Gemini 2.0 Flash)")
st.markdown("Upload a **PDF** or **text file**, or paste content to generate a **summary**, **key takeaways**, and **tags**.")

# Choose input method
input_mode = st.radio("Select input method:", ["Upload PDF", "Upload TXT", "Paste Text"])
book_content = ""

# ========================== #
# 📄 File or Text Handling
# ========================== #
if input_mode == "Upload PDF":
    uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_pdf is not None:
        try:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in reader.pages:
                book_content += page.extract_text()
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

elif input_mode == "Upload TXT":
    uploaded_txt = st.file_uploader("Upload a text file", type=["txt"])
    if uploaded_txt is not None:
        try:
            book_content = uploaded_txt.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading text file: {e}")

else:
    book_content = st.text_area("Paste the book chapter or content here:")

# ========================== #
# 🚀 Generate Summary Button
# ========================== #
if st.button("Generate Summary"):
    if not book_content.strip():
        st.warning("Please upload or enter some content.")
    else:
        with st.spinner("Summarizing with Gemini 2.0 Flash..."):

            # Prompt for Gemini
            prompt_text = f"""
You are an expert book summarizer. Given the following content, return:
1. A concise summary
2. 3 to 5 bullet-point key takeaways
3. 5 relevant hashtags or tags

Content:
\"\"\"
{book_content[:12000]}
\"\"\"
"""

            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": prompt_text}]
                }]
            }

            try:
                response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)

                if response.status_code == 200:
                    result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.success("✅ Summary generated!")
                    st.markdown(result_text)

                    # Send to webhook (if configured)
                    if WEBHOOK_URL.strip().startswith("http"):
                        webhook_payload = {
                            "summary": result_text,
                            "source": "BookSummaryApp"
                        }
                        webhook_response = requests.post(WEBHOOK_URL, json=webhook_payload)
                        if webhook_response.status_code in [200, 201]:
                            st.info("📬 Sent summary to webhook successfully.")
                        else:
                            st.warning(f"⚠️ Webhook failed with status {webhook_response.status_code}")

                else:
                    st.error(f"Gemini API Error: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"❌ Failed to fetch summary: {e}")
