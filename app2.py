from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

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
                        a.textContent = `${format.resolution} (${format.ext})`;
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

# Route to get video formats
@app.route('/get_video_formats', methods=['POST'])
def get_video_formats():
    try:
        youtube_url = request.form.get('url')
        if not youtube_url:
            return jsonify({'error': 'No URL provided'}), 400

        ydl_opts = {'quiet': True}
        formats_list = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            formats = info.get('formats', [])

            # Filter for the desired resolutions and create the response
            for f in formats:
                if f.get('height') in [1080, 720, 480] and f.get('url'):
                    formats_list.append({
                        'resolution': f"{f['height']}p",
                        'ext': f['ext'],
                        'url': f['url']
                    })

        if not formats_list:
            return jsonify({'error': 'No suitable formats found'}), 404

        return jsonify({'formats': formats_list}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred on the server'}), 500

if __name__ == '__main__':
    app.run(debug=True)
