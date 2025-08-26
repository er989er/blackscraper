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
    "dl (description list)": "dl",
    "dt (description term)": "dt",
    "em (emphasized text)": "em",
    "embed (embedded content)": "embed",
    "fieldset (form group)": "fieldset",
    "figcaption (caption for figure)": "figcaption",
    "figure (figure with media)": "figure",
    "footer (footer section)": "footer",
    "form (form container)": "form",
    "h1 (main heading)": "h1",
    "h2 (section heading)": "h2",
    "h3 (subsection heading)": "h3",
    "h4 (smaller heading)": "h4",
    "h5 (tiny heading)": "h5",
    "h6 (smallest heading)": "h6",
    "head (document head)": "head",
    "header (page header)": "header",
    "hr (horizontal rule)": "hr",
    "html (root element)": "html",
    "i (italic text - stylistic)": "i",
    "iframe (inline frame)": "iframe",
    "img (image element)": "img",
    "input (form input field)": "input",
    "ins (inserted text)": "ins",
    "kbd (keyboard input)": "kbd",
    "label (form label)": "label",
    "legend (form legend)": "legend",
    "li (list item)": "li",
    "link (external resource link)": "link",
    "main (main content)": "main",
    "map (image map)": "map",
    "mark (highlighted text)": "mark",
    "meta (metadata)": "meta",
    "meter (measurement scalar)": "meter",
    "nav (navigation links)": "nav",
    "noscript (fallback for no JS)": "noscript",
    "object (embedded object)": "object",
    "ol (ordered list)": "ol",
    "optgroup (group of options in select)": "optgroup",
    "option (select option)": "option",
    "output (output value)": "output",
    "p (paragraph)": "p",
    "picture (responsive images)": "picture",
    "pre (preformatted text)": "pre",
    "progress (progress indicator)": "progress",
    "q (short inline quote)": "q",
    "rp (ruby fallback parenthesis)": "rp",
    "rt (ruby annotation)": "rt",
    "ruby (ruby annotation)": "ruby",
    "s (strikethrough text)": "s",
    "samp (sample output)": "samp",
    "script (script code)": "script",
    "section (document section)": "section",
    "select (dropdown menu)": "select",
    "small (small text)": "small",
    "source (media source)": "source",
    "span (inline container)": "span",
    "strong (strong importance)": "strong",
    "style (style info)": "style",
    "sub (subscript text)": "sub",
    "summary (summary for details)": "summary",
    "sup (superscript text)": "sup",
    "svg (SVG graphics)": "svg",
    "table (table element)": "table",
    "tbody (table body)": "tbody",
    "td (table cell)": "td",
    "template (template content)": "template",
    "textarea (multiline input)": "textarea",
    "tfoot (table footer)": "tfoot",
    "th (table header cell)": "th",
    "thead (table header)": "thead",
    "time (time or date)": "time",
    "title (document title)": "title",
    "tr (table row)": "tr",
    "track (text tracks for media)": "track",
    "u (underlined text)": "u",
    "ul (unordered list)": "ul",
    "var (variable)": "var",
    "video (video content)": "video",
    "wbr (word break opportunity)": "wbr"
}

selected_expert = st.multiselect(
    "⚡ Expert Tags (full HTML5 elements):",
    options=list(expert_tags.keys())
)

# Collect all chosen tags
tags = [beginner_tags[t] for t in selected_beginner] + [expert_tags[t] for t in selected_expert]

# Allow custom tags
custom_tags_input = st.text_input("Or enter custom tags (comma-separated):")
if custom_tags_input.strip():
    tags.extend([t.strip() for t in custom_tags_input.split(",")])

# --- URL INPUT ---
url = st.text_input("Enter Website URL:")

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
                        if tag == "img" and element.has_attr("src"):
                            text = element["src"]
                        elif tag == "a" and element.has_attr("href"):
                            text = element["href"]
                        else:
                            text = element.get_text(strip=True)
                        if text:
                            results.append(f"<{tag}>: {text}")

                if results:
                    st.subheader("First 50 Results")
                    for item in results[:50]:
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
