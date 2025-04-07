import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO



st.set_page_config(page_title="Book Scraping By Sweeta", layout="centered")
st.title("Let's Scrape Data from BooktoScrape.com URL: ")

st.markdown("Enter a URL like: `http://books.toscrape.com/` not that `https://books.toscrape.com/`")

url = st.text_input("Enter URL: ")

def scrapedata(baseUrl):
    books = []
    while baseUrl:
        response = requests.get(baseUrl)
        sp = BeautifulSoup(response.content, 'html.parser')

        articles = sp.find_all('article', class_='product_pod')

        for article in articles:
            title = article.h3.a['title']
            price = article.find('p', class_='price_color').text

            books.append({
                "Title": title,
                "Price": price
            })
        next_button = sp.find('li', class_='next')
        if next_button:
            next_url = next_button.a['href']
            baseUrl = baseUrl.rsplit('/', 1)[0] + '/' + next_url
        else:
            baseUrl = None

    return pd.DataFrame(books)

# When button is clicked
if st.button("Scrape and Export to Excel"):
    if url.strip() == "":
        st.error("Please enter a valid URL.")
    else:
        try:
            df = scrapedata(url)

            if df.empty:
                st.warning("No books found. Please check the URL.")
            else:
                st.success(f"Scraped {len(df)} books successfully!")

                st.dataframe(df, use_container_width=True)

                # Create Excel in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Books')

                st.download_button(
                    label="📥 Download Excel File",
                    data=output.getvalue(),
                    file_name="book_titles_prices.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")
