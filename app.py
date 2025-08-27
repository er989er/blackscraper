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
"div (generic container)": "div",
st.error(f"An error occurred: {e}")
