from bs4 import BeautifulSoup


def inject_icons_in_list_items(html_body: str, icon_url: str) -> str:
    soup = BeautifulSoup(html_body, "html.parser")

    for ul in soup.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            # Create the <img> tag
            img_tag = soup.new_tag("img", src=icon_url, alt="check", width="20", height="20")
            img_tag['style'] = "margin-right: 8px;"

            # Inject <img> at the start of the <li>
            li.insert(0, img_tag)
    return str(soup)


def add_padding_to_p_before_ul_or_a(html_body: str) -> str:
    soup = BeautifulSoup(html_body, "html.parser")

    # Loop through all <p> tags
    for p_tag in soup.find_all("p"):
        next_sibling = p_tag.find_next_sibling()

        # Check if the next non-empty sibling is <ul> or <a>
        while next_sibling and (str(next_sibling).strip() == '' or next_sibling.name is None):
            next_sibling = next_sibling.find_next_sibling()

        if next_sibling and next_sibling.name in ['ul', 'a']:
            # Get existing style or create one
            existing_style = p_tag.get("style", "")
            if "padding-bottom" not in existing_style:
                # Append padding-bottom
                updated_style = existing_style.rstrip(";") + "; padding-bottom: 16px;"
                p_tag['style'] = updated_style.strip()
    return str(soup)
