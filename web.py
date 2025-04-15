import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import streamlit as st
from datetime import datetime
import pandas as pd
import json

# Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
MAX_PAGES = 50  # Limit to prevent excessive scraping
REQUEST_DELAY = 1  # Delay between requests in seconds

class WebScraper:
    def __init__(self):
        self.visited_urls = set()
        self.scraped_data = []
        self.domain = ""
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the same domain."""
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc == self.domain and parsed.scheme in ['http', 'https']
    
    def get_all_website_links(self, url):
        """Get all links from a webpage that belong to the same domain."""
        links = set()
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                
                # Remove fragments and query parameters for simplicity
                full_url = full_url.split('#')[0].split('?')[0]
                
                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    links.add(full_url)
                    
        except Exception as e:
            st.warning(f"Error processing {url}: {str(e)}")
            
        return links
    
    def scrape_page(self, url):
        """Scrape content from a single page."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'iframe']):
                element.decompose()
            
            # Get page title
            title = soup.title.string if soup.title else "No Title"
            
            # Get main content (simplified approach)
            main_content = soup.find('main') or soup.find('article') or soup.body
            text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""
            
            # Count links
            links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
            internal_links = [link for link in links if self.is_valid_url(link)]
            external_links = [link for link in links if not self.is_valid_url(link) and bool(urlparse(link).netloc)]
            
            # Count images
            images = len(soup.find_all('img'))
            
            # Save scraped data
            page_data = {
                'url': url,
                'title': title,
                'content': text_content,
                'internal_links': len(internal_links),
                'external_links': len(external_links),
                'images': images,
                'timestamp': datetime.now().isoformat(),
                'word_count': len(text_content.split())
            }
            
            self.scraped_data.append(page_data)
            return True
            
        except Exception as e:
            st.warning(f"Error scraping {url}: {str(e)}")
            return False
    
    def crawl_website(self, start_url, max_pages=MAX_PAGES):
        """Crawl website starting from the given URL."""
        parsed = urlparse(start_url)
        self.domain = parsed.netloc
        
        queue = [start_url]
        self.visited_urls.add(start_url)
        
        processed_pages = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        while queue and processed_pages < max_pages:
            current_url = queue.pop(0)
            
            status_text.text(f"Processing: {current_url} ({processed_pages}/{max_pages} pages)")
            progress_bar.progress(processed_pages / max_pages)
            
            if self.scrape_page(current_url):
                processed_pages += 1
                
                # Get links from current page
                new_links = self.get_all_website_links(current_url)
                
                # Add new links to queue
                for link in new_links:
                    if link not in self.visited_urls:
                        self.visited_urls.add(link)
                        queue.append(link)
            
            time.sleep(REQUEST_DELAY)
        
        progress_bar.empty()
        status_text.empty()
        
        return processed_pages
    
    def generate_report(self, format_type='html'):
        """Generate report in specified format."""
        if not self.scraped_data:
            return None
            
        if format_type == 'html':
            report = "<html><head><title>Web Scraping Report</title></head><body>"
            report += f"<h1>Web Scraping Report</h1>"
            report += f"<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
            report += f"<p>Total pages scraped: {len(self.scraped_data)}</p>"
            
            for page in self.scraped_data:
                report += f"<h2><a href='{page['url']}'>{page['title']}</a></h2>"
                report += f"<p><strong>URL:</strong> {page['url']}</p>"
                report += f"<p><strong>Word Count:</strong> {page['word_count']}</p>"
                report += f"<p><strong>Internal Links:</strong> {page['internal_links']}</p>"
                report += f"<p><strong>External Links:</strong> {page['external_links']}</p>"
                report += f"<p><strong>Images:</strong> {page['images']}</p>"
                report += f"<h3>Content Preview:</h3>"
                report += f"<div style='border:1px solid #ccc; padding:10px; max-height:200px; overflow:auto;'>"
                report += f"<pre>{page['content'][:2000]}{'...' if len(page['content']) > 2000 else ''}</pre>"
                report += f"</div><hr>"
            
            report += "</body></html>"
            return report
            
        elif format_type == 'json':
            return json.dumps({
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_pages': len(self.scraped_data)
                },
                'pages': self.scraped_data
            }, indent=2)
            
        elif format_type == 'csv':
            df = pd.DataFrame(self.scraped_data)
            return df.to_csv(index=False)
            
        elif format_type == 'excel':
            df = pd.DataFrame(self.scraped_data)
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False)
            writer.close()
            return output.getvalue()
            
        return None

def main():
    st.set_page_config(page_title="Web Scraper", page_icon="🌐", layout="wide")
    
    st.title("🌐 Advanced Web Scraper")
    st.markdown("""
    This tool scrapes websites including all their subpages and generates comprehensive reports.
    Enter a starting URL below and configure the scraping options.
    """)
    
    with st.form("scraper_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            start_url = st.text_input("Website URL to scrape", placeholder="https://example.com")
            max_pages = st.number_input("Maximum pages to scrape", min_value=1, max_value=500, value=50)
            
        with col2:
            report_format = st.selectbox("Report Format", ['html', 'json', 'csv', 'excel'])
            include_content = st.checkbox("Include full content in report", value=True)
            
        submitted = st.form_submit_button("Start Scraping")
    
    if submitted:
        if not start_url:
            st.error("Please enter a valid URL")
            return
            
        scraper = WebScraper()
        
        with st.spinner("Scraping website. This may take a while..."):
            scraped_count = scraper.crawl_website(start_url, max_pages)
        
        st.success(f"Successfully scraped {scraped_count} pages!")
        
        # Generate and display report
        report = scraper.generate_report(report_format)
        
        if report is None:
            st.error("No data was scraped. Please check the URL and try again.")
            return
        
        st.subheader("Scraping Report")
        
        if report_format == 'html':
            st.components.v1.html(report, height=800, scrolling=True)
        elif report_format == 'json':
            st.code(report, language='json')
        elif report_format == 'csv':
            st.dataframe(pd.read_csv(StringIO(report)))
        elif report_format == 'excel':
            st.download_button(
                label="Download Excel Report",
                data=report,
                file_name="web_scraping_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Download buttons
        st.subheader("Download Report")
        
        if report_format != 'excel':  # Excel already has its own download button
            st.download_button(
                label=f"Download as {report_format.upper()}",
                data=report,
                file_name=f"web_scraping_report.{report_format}",
                mime="text/html" if report_format == 'html' else "text/plain"
            )
        
        # Show summary statistics
        if scraper.scraped_data:
            st.subheader("Summary Statistics")
            df = pd.DataFrame(scraper.scraped_data)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Pages Scraped", len(df))
                st.metric("Average Word Count", int(df['word_count'].mean()))
                
            with col2:
                st.metric("Total Internal Links", df['internal_links'].sum())
                st.metric("Average Internal Links", int(df['internal_links'].mean()))
                
            with col3:
                st.metric("Total External Links", df['external_links'].sum())
                st.metric("Average External Links", int(df['external_links'].mean()))
            
            # Show URL list
            st.subheader("Scraped Pages")
            st.dataframe(df[['url', 'title', 'word_count']])

if __name__ == "__main__":
    from io import StringIO, BytesIO
    main()