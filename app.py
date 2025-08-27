import requests
from bs4 import BeautifulSoup
import streamlit as st

# --- PAGE CONFIG & DARK MODE STYLING ---
st.set_page_config(page_title="Black Scraper", layout="wide")
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
st.title("Black Scraper (Dark Mode)")

# --- USER INPUT ---
url = st.text_input("Enter Website URL:")
tags_input = st.text_input("HTML tags to scrape (comma-separated, default=h1,h2,h3,p):", "h1,h2,h3,p")
tags = [t.strip() for t in tags_input.split(",")]

# --- SLIDER FOR NUMBER OF RESULTS ---
max_results = st.slider("Number of results to display", min_value=1, max_value=100, value=50)

# --- SCRAPE & DISPLAY ---
if st.button("Scrape Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(url, headers=headers, timeout=10)

            # --- HANDLE BLOCKED OR FAILED REQUESTS ---
            if response.status_code == 403:
                st.error("Access denied (403). This site may block automated requests.")
            elif response.status_code == 429:
                st.error("Too many requests (429). Try again later.")
            elif response.status_code != 200:
                st.error(f"Failed to fetch page: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                for tag in tags:
                    for element in soup.find_all(tag):
                        if tag == "a" and element.has_attr("href"):
                            results.append(f'<a href="{element["href"]}" target="_blank">{element.get_text(strip=True)}</a>')
                        else:
                            text = element.get_text(strip=True)
                            if text:
                                results.append(f"<{tag}>: {text}")

                if results:
                    st.subheader(f"First {max_results} Results")
                    for item in results[:max_results]:
                        if item.startswith("<a"):
                            st.markdown(item, unsafe_allow_html=True)
                        else:
                            st.write(item)

                    content = "\n\n".join(results)
                    st.download_button(
                        label="Download Results as TXT",
                        data=content,
                        file_name="scraped_content.txt",
                        mime="text/plain"
                    )
                else:
                    st.info("No content found for the specified tags.")

        except requests.exceptions.Timeout:
            st.error("Request timed out. The site may be slow or unresponsive.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
