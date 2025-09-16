import re
import sys
import time
import random
from dataclasses import dataclass
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class Place:
    name: Optional[str] = None
    rating: Optional[str] = None
    reviews: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    plus_code: Optional[str] = None


def human_delay(a=0.4, b=0.9):
    time.sleep(random.uniform(a, b))


def norm_text(s: Optional[str]) -> Optional[str]:
    if not s:
        return s
    s = s.strip()
    s = s.replace("\u202f", " ").replace(",", ".")
    return re.sub(r"\s+", " ", s)


def extract_in_detail_panel(driver) -> Place:
    place = Place()

    try:
        h1 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
        )
        place.name = norm_text(h1.text)
    except Exception:
        pass

    try:
        info_block = driver.find_element(By.CSS_SELECTOR, ".skqShb, .LBgpqf")
        txt = norm_text(info_block.text)
        if txt:
            m_rating = re.search(r"(\d+(?:\.\d+)?)", txt)
            if m_rating:
                place.rating = m_rating.group(1)
            m_reviews = re.search(r"\(?(\d{1,6})\)?\s*(reviews?|yorum|review)", txt, re.I)
            if m_reviews:
                place.reviews = m_reviews.group(1)
            else:
                m_paren = re.search(r"\((\d{1,6})\)", txt)
                if m_paren:
                    place.reviews = m_paren.group(1)
    except Exception:
        pass

    try:
        addr_btn = driver.find_element(By.XPATH, "//button[@data-item-id='address']//div[contains(@class,'Io6YTe')]")
        place.address = norm_text(addr_btn.text)
    except Exception:
        pass

    try:
        phone_btn = driver.find_element(By.XPATH, "//button[starts-with(@data-item-id, 'phone:tel:')]//div[contains(@class,'Io6YTe')]")
        place.phone = norm_text(phone_btn.text)
    except Exception:
        pass

    try:
        plus_btn = driver.find_element(By.XPATH, "//button[@data-item-id='oloc']//div[contains(@class,'Io6YTe')]")
        place.plus_code = norm_text(plus_btn.text)
    except Exception:
        pass

    return place


def open_maps_and_search(driver, query_text: str):
    driver.get("https://www.google.com/maps?hl=en")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "searchboxinput"))
    )
    human_delay()
    box = driver.find_element(By.ID, "searchboxinput")
    box.clear()
    box.send_keys(query_text)
    human_delay()
    box.send_keys(Keys.ENTER)
    WebDriverWait(driver, 20).until(
        EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.Nv2PK"))
        )
    )
    human_delay(0.8, 1.4)


def collect_results(driver, limit: int) -> List[Place]:
    results: List[Place] = []
    seen = set()
    last_count = -1
    stagnant_rounds = 0

    while len(results) < limit:
        cards = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
        if not cards:
            try:
                results.append(extract_in_detail_panel(driver))
            except Exception:
                pass
            break

        for idx, card in enumerate(cards):
            if len(results) >= limit:
                break
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
                human_delay(0.25, 0.6)
                key = norm_text(card.text) or f"card-{idx}-{time.time()}"
                if key in seen:
                    continue
                seen.add(key)
                card.click()
                human_delay(0.7, 1.5)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
                    )
                except Exception:
                    pass
                place = extract_in_detail_panel(driver)
                if not place.name:
                    continue
                results.append(place)
                human_delay(0.5, 1.2)
            except Exception:
                continue

        if len(results) >= limit:
            break
        try:
            feed = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;", feed)
        except Exception:
            if cards:
                driver.execute_script("arguments[0].scrollIntoView({block:'end'});", cards[-1])
        human_delay(0.8, 1.4)

        if last_count == len(seen):
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
        last_count = len(seen)
        if stagnant_rounds >= 2:
            break

    return results[:limit]


def print_table(items: List[Place]):
    rows = []
    headers = ["#", "Name", "Rating", "Reviews", "Address", "Phone", "Plus code"]
    rows.append(headers)

    for i, it in enumerate(items, 1):
        rows.append([
            str(i),
            it.name or "",
            it.rating or "",
            it.reviews or "",
            it.address or "",
            it.phone or "",
            it.plus_code or "",
        ])

    widths = [max(len(str(row[c])) for row in rows) for c in range(len(headers))]

    def fmt_row(r):
        return " | ".join(str(r[c]).ljust(widths[c]) for c in range(len(headers)))

    sep = "-+-".join("-" * w for w in widths)
    print(fmt_row(rows[0]))
    print(sep)
    for r in rows[1:]:
        print(fmt_row(r))


def build_driver(headless: bool = False) -> webdriver.Chrome:
    chrome_opts = Options()
    if headless:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--lang=en-US")
    chrome_opts.add_argument("--window-size=1280,900")
    chrome_opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=chrome_opts)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(2)
    return driver


def main():
    try:
        print("Category (e.g., Hotel): ", end="", flush=True)
        category = input().strip()
        print("Location (e.g., Seattle): ", end="", flush=True)
        location = input().strip()
        print("Limit (e.g., 30): ", end="", flush=True)
        try:
            limit = int(input().strip())
        except Exception:
            limit = 20

        if not category or not location:
            print("Category and Location are required.", file=sys.stderr)
            sys.exit(1)

        query = f"{category} in {location}"
        driver = build_driver(headless=False)
        try:
            open_maps_and_search(driver, query)
            items = collect_results(driver, limit=limit)
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        if not items:
            print("No results found.")
            return

        print_table(items)

    except KeyboardInterrupt:
        print("\nAborted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
