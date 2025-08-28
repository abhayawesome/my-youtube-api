from flask import Flask, request, jsonify
from pytubefix import YouTube
import logging

# Set up logging to print detailed error information
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/api/get_audio', methods=['GET'])
def get_audio_handler():
    video_id = request.args.get('video_id')
    logging.info(f"Received request for video_id: {video_id}")

    if not video_id:
        logging.error("Request failed: 'video_id' parameter was not provided.")
        return jsonify({"error": "The 'video_id' parameter is required."}), 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        logging.info("Creating YouTube object...")
        yt = YouTube(youtube_url)
        logging.info(f"Successfully created YouTube object for title: {yt.title}")

        logging.info("Filtering for audio streams...")
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        
        if not audio_streams:
            logging.warning(f"No audio-only streams found for video_id: {video_id}")
            return jsonify({"error": "No audio-only streams found for this video."}), 404
        
        logging.info(f"Found {len(audio_streams)} audio streams. Preparing response...")
        formats = []
        for stream in audio_streams:
            # Handle cases where bitrate (abr) might be None
            bitrate_str = stream.abr if stream.abr else "0kbps"
            bitrate_val = int(bitrate_str.replace('kbps', '')) * 1000
            
            formats.append({
                "url": stream.url,
                "mimeType": stream.mime_type,
                "bitrate": bitrate_val
            })
        
        logging.info("Successfully prepared formats. Sending JSON response.")
        return jsonify(formats)

    except Exception as e:
        # Log the full, detailed exception traceback
        logging.exception(f"An unexpected error occurred for video_id: {video_id}")
        
        error_message = str(e)
        if "unavailable" in error_message.lower():
            return jsonify({"error": "This video is unavailable."}), 404
        
        # Return a more detailed error message for debugging
        return jsonify({
            "error": "An internal server error occurred.", 
            "details": error_message
        }), 500
