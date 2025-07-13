# app.py

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_you_should_change'
    # You'll add other configurations here later, like paths to databases
    DATABASE_DIR = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    SQLITE_DB_PATH = os.path.join(DATABASE_DIR, 'datanest.db')
    CHROMADB_PATH = os.path.join(DATABASE_DIR, 'chromadb_data')

app = Flask(__name__)
app.config.from_object(Config)

# --- Import Database Functions (will be in db.py) ---
# We'll import these once db.py is created
# from db import init_db, add_source_to_db, get_sources_from_db, get_bedrock_content_from_db, update_bedrock_content_in_db

# --- Initialize Database (Call this when app starts) ---
# with app.app_context():
#     init_db() # This will create tables if they don't exist


@app.route('/')
def index():
    """Serves the main DataNest HTML page."""
    return render_template('DataNest.html')

# --- API Endpoints ---

@app.route('/api/add_source', methods=['POST'])
def add_source():
    """
    Receives new source data from the frontend (URL or manual text).
    Performs initial processing and saves to the database.
    """
    data = request.json
    link = data.get('link')
    title = data.get('title')
    tags = data.get('tags', [])
    source_type = data.get('source_type') # 'url' or 'manual'
    content = data.get('content', '') # For manual input

    # Placeholder for actual content extraction and saving to DB
    # In a later step, we'll implement:
    # - Web scraping (requests, BeautifulSoup) for 'url' type
    # - PDF text extraction (PyPDF2) for '.pdf' links
    # - Placeholder for thumbnail generation
    # - Saving to SQLite
    # - Generating and saving embeddings to ChromaDB

    # For now, just simulate success and store basic data
    # THIS IS TEMPORARY and will be replaced by actual DB operations
    if source_type == 'url':
        # Simulate fetching title (backend-side now)
        # In real implementation, this would involve actual web scraping
        if not title and link:
            try:
                import requests
                from bs4 import BeautifulSoup
                res = requests.get(link, timeout=5)
                res.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.title.string if soup.title else "No Title Found"
            except Exception as e:
                print(f"Error fetching title for {link}: {e}")
                title = f"Untitled - {link}"

        # Simulate content extraction for URL
        if not content and link:
            try:
                import requests
                from bs4 import BeautifulSoup
                res = requests.get(link, timeout=5)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, 'html.parser')
                # A very basic attempt to get main content
                content = ' '.join(p.get_text() for p in soup.find_all('p'))
                if len(content) < 100: # If too little text, try body
                    content = soup.body.get_text()
                content = content[:5000] + "..." if len(content) > 5000 else content # Limit content size
            except Exception as e:
                print(f"Error extracting content for {link}: {e}")
                content = f"Could not extract content from {link}."


        # Simulate thumbnail (generic placeholder for now)
        if link and '.pdf' in link.lower():
            thumbnail_url = 'https://placehold.co/90x100?text=PDF'
        elif link and ('youtube.com' in link or 'vimeo.com' in link):
            thumbnail_url = 'https://placehold.co/90x100?text=Video'
        else:
            thumbnail_url = 'https://placehold.co/90x100?text=Article'

    else: # manual type
        link = "N/A" # No link for manual input
        thumbnail_url = 'https://placehold.co/90x100?text=Manual'
        # Content is already provided in `data.get('content')`

    # Simulate adding to DB
    # This will be replaced by add_source_to_db(link, title, tags, source_type, content, thumbnail_url, ...)
    print(f"Simulating saving source: Title: {title}, Link: {link}, Type: {source_type}, Tags: {tags}")

    # In a real scenario, you'd add this to your database and get an ID.
    # For now, we'll just return a success message.
    return jsonify({'message': 'Source saved successfully (placeholder)!', 'source': {'title': title, 'link': link, 'tags': tags, 'type': source_type, 'date': 'Today', 'thumbnail': thumbnail_url}}), 200

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """
    Returns a list of sources from the database based on filter.
    """
    source_type_filter = request.args.get('type', 'All')

    # Placeholder for actual database retrieval
    # This will be replaced by get_sources_from_db(source_type_filter)
    # For now, return some dummy data
    dummy_sources = [
        {"id": 1, "title": "Understanding Nature-Based Solutions in Cities", "link": "https://example.com/nps-cities", "tags": ["Nature-Based Solutions", "Urban"], "type": "Article", "date": "2024-06-15", "thumbnail": "https://placehold.co/90x100?text=Article", "summary": "A comprehensive overview of NBS implementation in urban environments, highlighting benefits and challenges.", "novelty_score": 0.3},
        {"id": 2, "title": "New Framework for Biodiversity Credits", "link": "https://example.com/biodiversity-credits-new", "tags": ["Biodiversity/Carbon Credits", "Frameworks"], "type": "Article", "date": "2024-07-01", "thumbnail": "https://placehold.co/90x100?text=Article", "summary": "An innovative framework proposing a new mechanism for valuing biodiversity credits beyond carbon.", "novelty_score": 0.8, "ai_analysis": "This article presents a novel approach to biodiversity credit valuation, focusing on ecosystem services beyond carbon sequestration. It challenges current market structures by proposing a multi-metric valuation system, which could lead to more holistic conservation finance. The key innovation lies in its proposed 'biodiversity unit' which aggregates multiple ecological indicators rather than relying on a single one. This contrasts with existing carbon-centric models.", "controversy_points": ["Challenges the feasibility of multi-metric aggregation.", "Raises concerns about data standardization across diverse ecosystems."]},
        {"id": 3, "title": "PDF Guide: Investing in Marine Conservation", "link": "https://example.com/marine-conservation.pdf", "tags": ["Capital & Instruments", "Use Cases Nature Finance"], "type": "PDF", "date": "2024-06-20", "thumbnail": "https://placehold.co/90x100?text=PDF", "summary": "A detailed guide on various financial instruments applicable to marine conservation projects.", "novelty_score": 0.5},
        {"id": 4, "title": "Video: dMRV Technologies in Action", "link": "https://youtube.com/watch?v=dmrv-tech", "tags": ["dMRV Tools & Data", "Innovation ecosystem"], "type": "Video", "date": "2024-05-28", "thumbnail": "https://placehold.co/90x100?text=Video", "summary": "Presentation showcasing real-world applications of remote sensing and AI in environmental monitoring.", "novelty_score": 0.6},
        {"id": 5, "title": "Manual Entry: LinkedIn Post - Green Bonds Trends", "link": "N/A", "tags": ["Capital & Instruments"], "type": "Manual", "date": "2024-07-10", "thumbnail": "https://placehold.co/90x100?text=Manual", "summary": "Analysis of recent trends in green bond issuance and investor sentiment, highlighting a shift towards smaller, impact-focused issuances.", "novelty_score": 0.7}
    ]

    if source_type_filter == 'All':
        return jsonify(dummy_sources), 200
    else:
        filtered_sources = [s for s in dummy_sources if s['type'].lower() == source_type_filter.lower()]
        return jsonify(filtered_sources), 200

@app.route('/api/generate_brief', methods=['POST'])
def generate_brief():
    """
    Triggers the analysis of pending sources and generates the weekly brief.
    """
    # Placeholder for actual brief generation logic
    # This will involve:
    # - Retrieving 'pending_analysis' sources
    # - Running LLM analysis (with Bedrock filter)
    # - Compiling the brief HTML
    # - Saving the brief and returning its URL

    print("Simulating brief generation...")
    # For now, just return a dummy URL. In a real scenario, you'd save an HTML file.
    # This will be replaced by actual brief generation logic.
    dummy_brief_url = "/static/example_brief.html" # Assuming you'd serve a static file later

    # Create a dummy static brief file for testing
    brief_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Weekly Intelligence Brief - Dummy</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 20px auto; padding: 20px; border: 1px solid #eee; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #1a1a1a; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }
        h2 { color: #1a1a1a; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .source-item { background: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 5px; border: 1px solid #e1e1e1; }
        .source-item h3 { margin-top: 0; color: #0056b3; }
        .source-item .link { font-size: 0.9em; color: #0077cc; text-decoration: none; }
        .source-item .link:hover { text-decoration: underline; }
        .insight-category { margin-top: 15px; padding-left: 20px; border-left: 3px solid #0077cc; }
        .insight-category h4 { margin-top: 0; color: #0056b3; }
    </style>
    </head>
    <body>
        <h1>Weekly Intelligence Brief - Dummy (Generated: July 13, 2025)</h1>
        <p>This is a simulated brief generated by DataNest. Actual content will be much richer.</p>

        <h2>New Practical Implementations</h2>
        <div class="source-item">
            <h3>New Pilot for Ocean Carbon Sequestration</h3>
            <p>A recent pilot project in the North Sea successfully demonstrated a novel method for accelerating ocean carbon sequestration using enhanced alkalinity. The report details the specific chemical processes and the preliminary environmental impact assessments.</p>
            <p class="insight-category"><h4>Strategic Reframing:</h4> How might this technology be scaled for broader adoption in different oceanic regions, considering regulatory frameworks and local biodiversity impacts?</p>
            <p><a href="https://example.com/ocean-carbon-pilot" target="_blank" class="link">Source: Ocean Carbon Pilot Report</a></p>
        </div>

        <h2>Contrarian & Forward-Looking Insights</h2>
        <div class="source-item">
            <h3>Critique on Current ESG Rating Methodologies</h3>
            <p>An article from a prominent think tank argues that current ESG rating methodologies are fundamentally flawed, often overlooking actual ecological impact in favor of corporate governance and 'greenwashing' metrics. It proposes a radical shift towards outcomes-based ecological accounting.</p>
            <p class="insight-category"><h4>Strategic Reframing:</h4> If this critique is valid, how should investment strategy shift to genuinely align with ecological impact rather than just compliance? What new possibilities emerge for "true" sustainable finance?</p>
            <p><a href="https://example.com/esg-critique" target="_blank" class="link">Source: ESG Critique Article</a></p>
        </div>
    </body>
    </html>
    """

    # Ensure 'static' folder exists
    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    brief_path = os.path.join(static_dir, 'weekly_brief.html')
    with open(brief_path, 'w') as f:
        f.write(brief_content)

    return jsonify({'message': 'Brief generation initiated (placeholder)!', 'brief_url': '/static/weekly_brief.html'}), 200

@app.route('/api/bedrock_content', methods=['GET', 'POST'])
def bedrock_content():
    """
    Manages the Bedrock knowledge content.
    GET: Returns the current bedrock content.
    POST: Updates the bedrock content and regenerates embeddings.
    """
    # We'll implement the actual get_bedrock_content_from_db and update_bedrock_content_in_db here later.
    # For now, return/accept dummy content.
    if request.method == 'GET':
        dummy_bedrock = "This is placeholder bedrock knowledge. It covers basic concepts of nature finance, carbon sequestration principles, and common biodiversity conservation methods. It does not include specific company names or detailed project mechanics unless they are widely established industry standards."
        return jsonify({'content': dummy_bedrock}), 200
    elif request.method == 'POST':
        data = request.json
        new_content = data.get('content', '')
        # Here, you would save new_content to DB and regenerate embeddings
        print(f"Bedrock content updated (placeholder): {new_content[:100]}...")
        return jsonify({'message': 'Bedrock knowledge updated successfully (placeholder)!'}), 200


if __name__ == '__main__':
    app.run(debug=True) # debug=True is good for development, disable in production
