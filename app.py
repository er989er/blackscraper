# Save as app.py
import requests
from bs4 import BeautifulSoup
import streamlit as st

# --- PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Universal Web Scraper", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #000000;
        color: #00ffff;
    }
    .stButton>button {
        background-color: #0000ff;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #000000;
        color: #00ffff;
    }
    </style>
    """, unsafe_allow_html=True
)
st.title("🌐 Universal Web Scraper (Dark Mode)")

# --- USER INPUT ---
url = st.text_input("Enter Website URL:")
tags_input = st.text_input("HTML tags to scrape (comma-separated, default=h1,h2,h3,p):", "h1,h2,h3,p")
tags = [t.strip() for t in tags_input.split(",")]

# --- SCRAPE & DISPLAY ---
if st.button("Scrape Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                st.error(f"Failed to fetch page: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                for tag in tags:
                    for element in soup.find_all(tag):
                        text = element.get_text(strip=True)
                        if text:
                            results.append(f"<{tag}>: {text}")

                if results:
                    st.subheader("First 50 Results")
                    for item in results[:50]:
                        st.write(item)

                    # --- SAVE TO FILE ---
                    content = "\n\n".join(results)
                    st.download_button(
                        label="💾 Download Results as TXT",
                        data=content,
                        file_name="scraped_content.txt",
                        mime="text/plain"
                    )
                else:
                    st.info("No content found for the specified tags.")
        except Exception as e:
            st.error(f"Error: {e}")
