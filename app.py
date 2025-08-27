import streamlit as st
import requests
from bs4 import BeautifulSoup
import difflib

# --- URL input ---
url = st.text_input("Enter URL to scrape:")

# --- Tags to scrape ---
tags = ["h1","h2","h3","h4","h5","h6","p","a","img"]

# --- Slider for number of hits ---
num_hits = st.slider(
    "Number of search suggestions to show",
    min_value=1,
    max_value=50,
    value=5
)

# --- SCRAPE & DISPLAY HIERARCHICALLY WITH STYLED NESTED EXPANDERS + ICONS ---
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

                # --- Build nested hierarchy ---
                root = {"level": 0, "heading": None, "content": [], "children": []}
                stack = [root]

                for element in soup.find_all(tags):
                    if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                        level = int(element.name[1])
                        node = {"level": level, "heading": element.get_text(strip=True), "content": [], "children": []}
                        while stack and stack[-1]["level"] >= level:
                            stack.pop()
                        stack[-1]["children"].append(node)
                        stack.append(node)

                    elif element.name == "p":
                        text = element.get_text(strip=True)
                        if text:
                            stack[-1]["content"].append(text)
                    elif element.name == "img" and element.has_attr("src"):
                        stack[-1]["content"].append(f"[Image] {element['src']}")
                    elif element.name == "a" and element.has_attr("href"):
                        stack[-1]["content"].append(f"[Link] {element['href']}")

                # --- Color + Icon map for heading levels ---
                level_styles = {
                    1: {"color": "#00BFFF", "icon": "📘"},
                    2: {"color": "#32CD32", "icon": "📗"},
                    3: {"color": "#9370DB", "icon": "📕"},
                    4: {"color": "#FFD700", "icon": "📒"},
                    5: {"color": "#FF69B4", "icon": "📓"},
                    6: {"color": "#FF4500", "icon": "📔"},
                }

                # --- Recursive function to display nested expanders ---
                def display_node(node, indent=0):
                    if node["heading"]:
                        style = level_styles.get(node["level"], {"color": "#FFFFFF", "icon": "📄"})
                        title = f"<span style='color:{style['color']}; margin-left:{indent*20}px;'>{style['icon']} {node['heading']}</span>"
                        with st.expander(title, expanded=False):
                            for c in node["content"]:
                                st.write(c)
                            for child in node["children"]:
                                display_node(child, indent + 1)
                    else:
                        for c in node["content"]:
                            st.write(c)
                        for child in node["children"]:
                            display_node(child, indent)

                # Render hierarchy
                display_node(root)

                # --- Flatten hierarchy to text for download ---
                def flatten_node(node, indent=0):
                    lines = []
                    if node["heading"]:
                        lines.append("  "*indent + node["heading"])
                    for c in node["content"]:
                        lines.append("  "*(indent+1) + c)
                    for child in node["children"]:
                        lines.extend(flatten_node(child, indent+1))
                    return lines

                all_lines = flatten_node(root)
                text_data = "\n".join(all_lines)

                # --- Add download button ---
                st.download_button(
                    label="Download Results as TXT",
                    data=text_data,
                    file_name="scraped_content.txt",
                    mime="text/plain"
                )

                # --- Search suggestions (adjusted by slider) ---
                search_query = st.text_input("Search text").strip()
                if search_query:
                    all_texts = [line.strip() for line in all_lines if line.strip()]
                    suggestions = difflib.get_close_matches(search_query, all_texts, n=num_hits, cutoff=0.5)
                    if suggestions:
                        st.info(f"Suggestions ({len(suggestions)} hits): {', '.join(suggestions)}")
                    else:
                        st.warning("No close matches found.")

        except requests.exceptions.Timeout:
            st.error("Request timed out. The site may be slow or unresponsive.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
