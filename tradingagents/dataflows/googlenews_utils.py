import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


def is_rate_limited(response):
    """Check if the response indicates rate limiting (status code 429)"""
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """Make a request with retry logic for rate limiting"""
    # Random delay before each request to avoid detection
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers)
    return response


def getNewsData(query, start_date, end_date):
    """
    Scrape Google News search results for a given query and date range.
    query: str - search query
    start_date: str - start date in the format yyyy-mm-dd or mm/dd/yyyy
    end_date: str - end date in the format yyyy-mm-dd or mm/dd/yyyy
    """
    if "-" in start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.strftime("%m/%d/%Y")
    if "-" in end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.strftime("%m/%d/%Y")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/101.0.4951.54 Safari/537.36"
        )
    }

    news_results = []
    page = 0
    while True:
        offset = page * 10
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start={offset}"
        )

        try:
            response = make_request(url, headers)
            soup = BeautifulSoup(response.content, "html.parser")
            # Try multiple selectors for news results as Google changes them frequently
            results_on_page = (soup.select("div.SoaBEf") or 
                              soup.select("div.Gx5Zad") or 
                              soup.select("div.g") or
                              soup.select("article") or
                              soup.select("[data-hveid]"))

            if not results_on_page:
                break  # No more results found

            for el in results_on_page:
                try:
                    # Extract link with fallback
                    link_el = el.find("a")
                    link = link_el["href"] if link_el and link_el.get("href") else "No link"
                    
                    # Extract title with multiple selector fallbacks
                    title_el = (el.select_one("div.MBeuO") or 
                               el.select_one(".MBeuO") or 
                               el.select_one("h3") or 
                               el.select_one(".LC20lb") or
                               el.select_one("[role='heading']"))
                    title = title_el.get_text().strip() if title_el else "No title"
                    
                    # Extract snippet with multiple selector fallbacks
                    snippet_el = (el.select_one(".GI74Re") or 
                                 el.select_one(".st") or 
                                 el.select_one(".s") or
                                 el.select_one("span"))
                    snippet = snippet_el.get_text().strip() if snippet_el else "No snippet"
                    
                    # Extract date with multiple selector fallbacks
                    date_el = (el.select_one(".LfVVr") or 
                              el.select_one(".f") or 
                              el.select_one("time") or
                              el.select_one("[datetime]"))
                    date = date_el.get_text().strip() if date_el else "No date"
                    
                    # Extract source with multiple selector fallbacks
                    source_el = (el.select_one(".NUnG9d span") or 
                                el.select_one(".NUnG9d") or 
                                el.select_one(".fG8Fp") or
                                el.select_one("cite"))
                    source = source_el.get_text().strip() if source_el else "Unknown source"
                    
                    # Only add result if we have at least a title and link
                    if title != "No title" and link != "No link":
                        news_results.append(
                            {
                                "link": link,
                                "title": title,
                                "snippet": snippet,
                                "date": date,
                                "source": source,
                            }
                        )
                except Exception as e:
                    print(f"Error processing result: {e}")
                    # If one of the fields is not found, skip this result
                    continue

            # Update the progress bar with the current count of results scraped

            # Check for the "Next" link (pagination)
            next_link = soup.find("a", id="pnnext")
            if not next_link:
                break

            page += 1

        except Exception as e:
            print(f"Failed after multiple retries: {e}")
            break

    return news_results
