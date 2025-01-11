from flask import Flask, request, jsonify
import yt_dlp as youtube_dl
import logging
import random
import time

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Simulated delay to mimic human-like behavior
def add_request_delay():
    time.sleep(random.randint(3, 7))  # Random delay between 3 to 7 seconds

# Function to get video formats using yt-dlp
def get_video_formats(url):
    ydl_opts = {
        'quiet': True,
        'format': 'best',  # Best format (you can adjust this for other formats)
        'extractaudio': True,  # Extract audio if needed
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        
        # Filter and return only the download URLs
        download_links = [
            {'resolution': format['format_note'], 'url': format['url']}
            for format in formats
            if 'url' in format
        ]
    return download_links

# Endpoint to get video formats
@app.route('/get_video_formats', methods=['POST'])
def get_video_formats_route():
    youtube_url = request.json.get('url')
    if not youtube_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    download_links = get_video_formats(youtube_url)
    if not download_links:
        return jsonify({'error': 'No download options available'}), 404
    
    return jsonify({'formats': download_links}), 200

# Serve the main page (HTML)
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Video Downloader</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #121212; color: #fff; padding: 50px 20px; }
            h1 { color: #28a745; font-size: 36px; }
            input, button { padding: 15px; width: 80%; margin: 10px 0; border-radius: 5px; }
            input { font-size: 16px; }
            button { background-color: #28a745; color: white; border: none; cursor: pointer; font-size: 18px; }
            button:hover { background-color: #218838; }
            #loading { display: none; color: #ffc107; font-size: 18px; }
            #download-section { display: none; margin-top: 20px; }
            #download-links a { color: #28a745; font-size: 18px; text-decoration: none; display: block; margin: 10px 0; }
            #download-links a:hover { text-decoration: underline; }
            footer { font-size: 14px; color: #aaa; margin-top: 50px; }
            footer a { color: #28a745; text-decoration: none; }
            footer a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>YouTube Video Downloader</h1>
        <form id="download-form">
            <input type="text" id="url" placeholder="Paste YouTube URL here..." required>
            <button type="submit">Get Download Links</button>
        </form>
        <div id="loading">Processing...</div>
        <div id="download-section">
            <h3>Available Download Options:</h3>
            <div id="download-links"></div>
        </div>
        <footer>
            Developed by <strong>@Hassan</strong><br>
            For contact, reach me on <a href="https://wa.me/393511289823" target="_blank">WhatsApp</a>
        </footer>
        <script>
            document.getElementById('download-form').addEventListener('submit', function (event) {
                event.preventDefault();
                const url = document.getElementById('url').value;
                const loading = document.getElementById('loading');
                const downloadSection = document.getElementById('download-section');
                const downloadLinks = document.getElementById('download-links');
                
                loading.style.display = 'block';
                downloadSection.style.display = 'none';
                downloadLinks.innerHTML = '';

                fetch('/get_video_formats', {
                    method: 'POST',
                    body: JSON.stringify({ 'url': url }),
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';

                    if (data.error) {
                        alert('Error: ' + data.error);
                        return;
                    }

                    downloadSection.style.display = 'block';
                    data.formats.forEach(format => {
                        const a = document.createElement('a');
                        a.href = format.url;
                        a.textContent = `Download (${format.resolution})`;
                        a.target = '_blank';
                        downloadLinks.appendChild(a);
                    });
                })
                .catch(error => {
                    loading.style.display = 'none';
                    alert('An error occurred. Please try again!');
                    console.error(error);
                });
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
