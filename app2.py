@app.route('/get_video_formats', methods=['POST'])
def get_video_formats():
    youtube_url = request.form.get('url')
    if not youtube_url:
        return jsonify({'error': 'No URL provided'}), 400

    # Extract the video ID from the YouTube URL
    video_id = youtube_url.split("v=")[-1].split("&")[0]

    # Set up the API headers
    headers = {
        "x-rapidapi-host": "ytstream-download-youtube-videos.p.rapidapi.com",
        "x-rapidapi-key": "38d94251c1mshb9e06a6431e3256p133708jsne945caa69315"  # Replace with your key
    }

    # Construct the API URL
    api_url = f"https://ytstream-download-youtube-videos.p.rapidapi.com/dl?id={video_id}"

    try:
        # Send a GET request to the API
        response = requests.get(api_url, headers=headers)

        # Check for HTTP errors
        if response.status_code != 200:
            return jsonify({'error': f"API Error: {response.status_code} - {response.text}"}), response.status_code

        # Parse the response JSON
        video_data = response.json()
        if 'error' in video_data:
            return jsonify({'error': video_data['error']}), 400

        # Extract download formats
        formats_list = []
        for resolution, url in video_data.get("formats", {}).items():
            if url:  # Ensure the URL is valid
                formats_list.append({
                    'resolution': resolution,
                    'url': url
                })

        # Return the formats
        if not formats_list:
            return jsonify({'error': 'No downloadable formats available.'}), 404

        return jsonify({'formats': formats_list}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500
