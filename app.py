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
st.title("Black Scraper")

# --- HOW TO USE TUTORIAL ---
with st.expander("📘 Tutorial: How to Use HTML Tags"):
    st.markdown("""
    **HTML tags tell the scraper what type of content you want to extract.**
    👉 Choose tags from the beginner or expert dropdowns below, or enter custom tags manually.

    - **Beginner Dropdown** → Common tags most people use (paragraphs, titles, links, images).
    - **Expert Dropdown** → Nearly all HTML tags with explanations.
    """)

# --- BEGINNER TAGS (common for scraping) ---
beginner_tags = {
    "p (paragraphs of text)": "p",
    "h1 (main heading)": "h1",
    "h2 (section heading)": "h2",
    "h3 (subsection heading)": "h3",
    "a (links)": "a",
    "img (images → URLs)": "img",
    "li (list item)": "li",
    "ul (unordered list)": "ul",
    "ol (ordered list)": "ol",
    "table (table element)": "table",
    "tr (table row)": "tr",
    "td (table cell)": "td"
}

selected_beginner = st.multiselect(
    "🔰 Beginner Tags (common & useful):",
    options=list(beginner_tags.keys()),
    default=["p (paragraphs of text)", "h1 (main heading)", "a (links)"]
)

# --- EXPERT TAGS (FULL HTML5 LIST) ---
expert_tags = {
    "a (hyperlink)": "a",
    "abbr (abbreviation)": "abbr",
    "address (contact information)": "address",
    "area (image map area)": "area",
    "article (self-contained content)": "article",
    "aside (sidebar content)": "aside",
    "audio (sound content)": "audio",
    "b (bold text - stylistic)": "b",
    "base (base URL for relative links)": "base",
    "bdi (bi-directional text isolate)": "bdi",
    "bdo (bi-directional text override)": "bdo",
    "blockquote (quoted block of text)": "blockquote",
    "body (document body)": "body",
    "br (line break)": "br",
    "button (clickable button)": "button",
    "canvas (graphics container)": "canvas",
    "caption (table caption)": "caption",
    "cite (citation reference)": "cite",
    "code (inline code snippet)": "code",
    "col (table column)": "col",
    "colgroup (group of table columns)": "colgroup",
    "data (machine-readable value)": "data",
    "datalist (list of options for input)": "datalist",
    "dd (description definition)": "dd",
    "del (deleted text)": "del",
    "details (expandable details widget)": "details",
    "dfn (definition term)": "dfn",
    "dialog (dialog box)": "dialog",
    "div (generic container)": "div"
}

selected_expert = st.multiselect(
    "🧠 Expert Tags (all HTML5 tags with explanations):",
    options=list(expert_tags.keys())
)

# --- COMBINE TAGS ---
custom_tags_input = st.text_input("Or enter custom tags (comma-separated):")
custom_tags = [t.strip() for t in custom_tags_input.split(",") if t.strip()]

# Merge all selected tags
final_tags = [beginner_tags[t] for t in selected_beginner] + \
             [expert_tags[t] for t in selected_expert] + custom_tags

# --- SLIDER FOR NUMBER OF RESULTS ---
max_results = st.slider("Number of results to display", min_value=1, max_value=100, value=50)

# --- URL INPUT & SCRAPE BUTTON ---
url = st.text_input("Enter Website URL:")

if st.button("Scrape Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                st.error(f"Failed to fetch page: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                for tag in final_tags:
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
