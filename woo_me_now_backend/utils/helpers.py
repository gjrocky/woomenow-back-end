import re
from urllib.parse import urlparse, urlencode

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


def style_otp(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    # Regex: match {{ otp }} with any spaces, case-insensitive
    # otp_pattern = re.compile(r"\{\{\s*otp\s*\}\}", re.IGNORECASE)
    otp_pattern = re.compile(r"\b\d{6}\b")

    for p in soup.find_all("p"):
        # Get raw inner HTML (not just text) so <strong> tags are preserved
        inner_html = "".join(str(child) for child in p.contents)

        if otp_pattern.search(inner_html):
            p["style"] = (
                "display:flex; gap:12px; font-weight:700; font-size:28px; "
                "line-height:34px; color:#FFFFFF; letter-spacing:14px"
            )
            break  # stop after first match (remove if you want all)

    return str(soup)


def replace_tracking_link(match, front_end_link, execution_id):
    original_url = match.group(1)
    if "woomenow.com" in original_url:
        parsed = urlparse(original_url)
        path_and_query = parsed.path
        if parsed.query:
            path_and_query += "?" + parsed.query
        clean_frontend = front_end_link.rstrip("/")
        new_url = f"{clean_frontend}{path_and_query}"
        query = urlencode({"redirect": new_url})
        tracking_href = f"{front_end_link}/track-email/{execution_id}/?{query}"
        return f'href="{tracking_href}"'
    return f'href="{original_url}"'


def replace_restaurant_id_and_respond_link(html_content: str, context_data: dict, execution_id: str,
                                           front_end_link: str):
    restaurant_id = context_data.get("restaurant")
    if restaurant_id:
        html_content = re.sub(r"\{\{\s*restaurant\s*\}\}", str(restaurant_id), html_content, flags=re.IGNORECASE)
        if execution_id:
            def replace_respond_link(match):
                original_url = match.group(1)
                if "woomenow.com/dashboard/restaurant" in original_url:
                    new_url = f"{front_end_link}dashboard/restaurant/{restaurant_id}/reviews?id={execution_id}"
                    return f'href="{new_url}"'
                return f'href="{original_url}"'

            html_content = re.sub(r'href="([^"]+)"', replace_respond_link, html_content)
    return html_content
