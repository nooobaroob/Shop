import logging
from flask import Flask, request, jsonify
import requests
import random
import time
import re

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Simulated delay to mimic human-like behavior
def add_request_delay():
    time.sleep(random.randint(3, 7))  # Random delay between 3 to 7 seconds

# Function to validate the YouTube URL and extract the video ID
def validate_youtube_url(url):
    app.logger.debug(f"Validating URL: {url}")  # Log the URL to see what is being passed
    match = re.match(r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+(?:v=|/)([^&?]+)", url)
    if match:
        video_id = match.group(4)
        app.logger.debug(f"Extracted Video ID: {video_id}")  # Log the extracted video ID
        return video_id
    return None

# Serve the main page
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

# Route to get video formats using RapidAPI
@app.route('/get_video_formats', methods=['POST'])
def get_video_formats():
    youtube_url = request.form.get('url')
    app.logger.debug(f"Received URL: {youtube_url}")  # Log the URL received from the frontend
    if not youtube_url:
        app.logger.error('No URL provided in the request.')
        return jsonify({'error': 'No URL provided'}), 400

    # Validate the YouTube URL and extract video ID
    video_id = validate_youtube_url(youtube_url)
    if not video_id:
        app.logger.error('Invalid YouTube URL or unable to extract video ID.')
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    # Set up API headers
    headers = {
        "x-rapidapi-host": "ytstream-download-youtube-videos.p.rapidapi.com",
        "x-rapidapi-key": "38d94251c1mshb9e06a6431e3256p133708jsne945caa69315"
    }

    # Construct the API URL
    api_url = f"https://ytstream-download-youtube-videos.p.rapidapi.com/dl?id={video_id}"
    app.logger.debug(f"API Request URL: {api_url}")  # Log the API request URL

    try:
        # Simulate human-like delay
        add_request_delay()

        # Send GET request to RapidAPI
        response = requests.get(api_url, headers=headers)

        # Log the response for debugging
        app.logger.debug(f"API Response: {response.status_code} - {response.text}")

        # Handle HTTP errors
        if response.status_code != 200:
            app.logger.error(f"API returned an error: {response.status_code}")
            return jsonify({'error': f"API Error: {response.status_code}"}), response.status_code

        # Parse the API response
        video_data = response.json()
        if 'error' in video_data:
            app.logger.error(f"API returned an error in response data: {video_data['error']}")
            return jsonify({'error': video_data['error']}), 400

        # Extract formats
        formats_list = [
            {'resolution': res, 'url': url}
            for res, url in video_data.get('formats', {}).items()
            if url
        ]

        if not formats_list:
            app.logger.warning('No download options available.')
            return jsonify({'error': 'No download options available.'}), 404

        return jsonify({'formats': formats_list}), 200

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
