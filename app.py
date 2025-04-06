
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def find_email_and_instagram(url):
    email = None
    instagram = None
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text()

        # Email
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        if emails:
            email = emails[0]

        # Instagram
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        insta_links = [l for l in links if 'instagram.com' in l]
        if insta_links:
            instagram = insta_links[0]
    except:
        pass
    return email, instagram

def scrape_shopify(keyword):
    results = []
    for page in range(1, 3):
        url = f"https://www.google.com/search?q={keyword}+site:myshopify.com&start={page*10}"
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup.find_all('a', href=True):
            if 'url?q=' in tag['href']:
                match = re.findall(r"url\?q=(https://[^&]*)", tag['href'])
                if match:
                    site_url = match[0]
                    email, insta = find_email_and_instagram(site_url)
                    results.append({
                        "Platform": "Shopify",
                        "Keyword": keyword,
                        "URL": site_url,
                        "Email": email,
                        "Instagram": insta
                    })
                    time.sleep(1)
    return results

def scrape_etsy(keyword):
    results = []
    for page in range(1, 3):
        url = f"https://www.etsy.com/search?q={keyword}&ref=pagination&page={page}"
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        shop_links = soup.select('a.shop-name')
        for link in shop_links:
            shop_url = link.get('href')
            if shop_url:
                email, insta = find_email_and_instagram(shop_url)
                results.append({
                    "Platform": "Etsy",
                    "Keyword": keyword,
                    "URL": shop_url,
                    "Email": email,
                    "Instagram": insta
                })
                time.sleep(1)
    return results

# Streamlit Web App
st.title("🧠 M.C. LeadMiner — AI-Enhanced Lead Scraper")
keyword = st.text_input("Enter a product niche keyword:", "skincare")

if st.button("Scrape Leads"):
    with st.spinner("Scraping in progress..."):
        shopify_data = scrape_shopify(keyword)
        etsy_data = scrape_etsy(keyword)
        all_data = shopify_data + etsy_data
        df = pd.DataFrame(all_data)
        st.success(f"Scraped {len(df)} leads!")
        st.dataframe(df)
        st.download_button("Download CSV", data=df.to_csv(index=False), file_name="leads.csv", mime="text/csv")
