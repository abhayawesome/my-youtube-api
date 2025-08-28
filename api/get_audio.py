from flask import Flask, request, jsonify
from pytubefix import YouTube

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)


@app.route('/api/get_audio', methods=['GET'])
def get_audio_handler():
    # Get the 'video_id' from the URL query parameters (e.g., ?video_id=dQw4w9WgXcQ)
    video_id = request.args.get('video_id')

    # --- Error Handling: Check if video_id was provided ---
    if not video_id:
        return jsonify({"error": "The 'video_id' parameter is required."}), 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        yt = YouTube(youtube_url)

        # Filter for only audio streams, order by quality (abr), highest first
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()

        # --- Error Handling: Check if any audio streams were found ---
        if not audio_streams:
            return jsonify({"error": "No audio-only streams found for this video."}), 404

        # Prepare the data in the format your Android app expects
        formats = []
        for stream in audio_streams:
            formats.append({
                "url": stream.url,
                "mimeType": stream.mime_type,
                "bitrate": int(stream.abr.replace('kbps', '')) * 1000  # Convert '128kbps' to 128000
            })

        # Return the list of formats as a JSON array
        return jsonify(formats)

    except Exception as e:
        # --- Generic Error Handling for any other issues ---
        error_message = str(e)
        if "unavailable" in error_message.lower():
            return jsonify({"error": "This video is unavailable."}), 404

        return jsonify({"error": "An internal server error occurred.", "details": error_message}), 500