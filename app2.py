from flask import Flask, request, jsonify
from pytube import YouTube
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

# Function to validate YouTube URL and extract video ID
def validate_youtube_url(url):
    logger.debug(f"Validating URL: {url}")
    try:
        # Attempt to create a YouTube object which validates the URL automatically
        yt = YouTube(url)
        return yt
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return None

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
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; background-color: #121212; color: #fff; }
            input { padding: 10px; width: 80%; margin: 10px 0; }
            button { padding: 10px 20px; background-color: #28a745; color: #fff; border: none; cursor: pointer; }
            button:hover { background-color: #218838; }
            #loading { display: none; color: #ffc107; margin-top: 10px; }
            #download-section { display: none; margin-top: 20px; }
            footer { margin-top: 40px; font-size: 14px; color: #aaa; }
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
                console.log("Sending URL to backend:", url);  // Log the URL for debugging
                const loading = document.getElementById('loading');
                const downloadSection = document.getElementById('download-section');
                const downloadLinks = document.getElementById('download-links');

                loading.style.display = 'block';
                downloadSection.style.display = 'none';
                downloadLinks.innerHTML = '';

                fetch('/get_video_formats', {
                    method: 'POST',
                    body: new URLSearchParams({ 'url': url }),
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
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
                        a.textContent = `${format.resolution}`;
                        a.style.display = 'block';
                        a.style.margin = '10px 0';
                        a.style.color = '#28a745';
                        a.style.textDecoration = 'none';
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

# Route to get video formats using Pytube
@app.route('/get_video_formats', methods=['POST'])
def get_video_formats():
    youtube_url = request.form.get('url')
    logger.debug(f"Received URL: {youtube_url}")
    
    if not youtube_url:
        logger.error('No URL provided in the request.')
        return jsonify({'error': 'No URL provided'}), 400

    yt = validate_youtube_url(youtube_url)
    if not yt:
        logger.error(f"Invalid URL: {youtube_url}")
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    logger.debug(f"Video ID: {yt.video_id}")

    # Get video streams (progressive streams contain both video and audio)
    streams = yt.streams.filter(progressive=True)

    formats_list = [
        {'resolution': stream.resolution, 'url': stream.url}
        for stream in streams
    ]

    if not formats_list:
        logger.warning('No download options available.')
        return jsonify({'error': 'No download options available.'}), 404

    return jsonify({'formats': formats_list}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
