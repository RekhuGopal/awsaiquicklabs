import wikipedia
from langchain_community.retrievers import WikipediaRetriever
from fpdf import FPDF

retriever = WikipediaRetriever(doc_content_chars_max=10000)

def download_wikipedia_pages(page_title):
    docs = retriever.get_relevant_documents(query=page_title) 
    if docs:
        content = docs[0].page_content
    return content

def save_as_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, title)
    pdf.ln(10)
    pdf.multi_cell(0, 10, content)
    filename = title.replace(" ", "_")
    pdf.output(f"./docs/{filename}.pdf")  # Use the title for the PDF filename

def download_wikipedia_pages_to_pdf(pages):
    for page_title in pages:
        content = download_wikipedia_pages(page_title)
        if content:
            content = content.encode('latin-1', 'replace').decode('latin-1')
            save_as_pdf(page_title, content)
            print(f"Downloaded and saved {page_title} as PDF.")

# List of Wikipedia pages to download
pages_to_download = ["Hong Kong", "London", "Singapore", "New York City"]  # Add more page titles as needed

download_wikipedia_pages_to_pdf(pages_to_download)
