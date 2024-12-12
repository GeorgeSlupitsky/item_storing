from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') 

# Configuration
MEMENTODB_API_KEY = os.getenv('MEMENTODB_API_KEY')
MEMENTODB_LIBRARY_IDS = json.loads(os.getenv('MEMENTODB_LIBRARY_IDS'))
DISCOGS_USER_TOKEN = os.getenv('DISCOGS_USER_TOKEN')

# Helper Classes
class BaseUploader:
    def __init__(self, library_id):
        self.library_id = library_id

    def create_entry(self, entry_data, photo_path):
        url = f'https://api.mementodatabase.com/v1/libraries/{self.library_id}/entries?token={MEMENTODB_API_KEY}'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(entry_data))
        if response.status_code == 201:
            entry_id = response.json().get('id')
            print(f"Entry created successfully with ID {entry_id}")
            # Upload photo after entry is created
            self.upload_photo(entry_id, photo_path)
        else:
            print(f"Error creating entry: {response.status_code}, {response.text}")

    def validate_inputs(self, description, photos):
        if len(description) > 10:
            raise ValueError("Description JSON must contain no more than 10 objects.")
        if len(photos) > 10:
            raise ValueError("You can upload a maximum of 10 photos.")

    def process_entry(self, entry, photo_path):
        raise NotImplementedError("Subclasses must implement this method.")        

class VinylsUploader(BaseUploader):
    def fetch_discogs_release(self, release_id):
        url = f"https://api.discogs.com/releases/{release_id}?token={DISCOGS_USER_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching release data from Discogs: {response.status_code}")
            return None

    def fetch_discogs_artist(self, artist_url):
        url = f"{artist_url}?token={DISCOGS_USER_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching artist data from Discogs: {response.status_code}")
            return None

    def upload_photo(self, entry_id, photo_path, field_id=20):
        url = f"https://api.mementodatabase.com/v1/libraries/{self.library_id}/entries/{entry_id}/files/{field_id}?token={MEMENTODB_API_KEY}"
        with open(photo_path, 'rb') as photo_file:
            files = {'file': photo_file}
            response = requests.post(url, files=files)
            if response.status_code == 201:
                print(f"Photo uploaded successfully for entry {entry_id}")
            else:
                print(f"Error uploading photo for entry {entry_id}: {response.status_code}, {response.text}")

    def process_entry(self, entry, photo_path):
        release_id = entry.get("ReleaseId")
        discogs_data = self.fetch_discogs_release(release_id)
        if not discogs_data:
            return

        artist_data = self.fetch_discogs_artist(discogs_data['artists'][0]['resource_url'])
        band_members = " ".join(member['name'].replace(" ", "") for member in artist_data['members']) if artist_data else ""

        entry_data = {
            "fields": [
                {"id": 1, "value": discogs_data['artists'][0]['name']},
                {"id": 2, "value": discogs_data['title']},
                {"id": 34, "value": entry["Sleeve Condition"]},
                {"id": 35, "value": entry["Media Condition"]},
                {"id": 32, "value": entry["Family"]},
                {"id": 30, "value": discogs_data['formats'][0]['qty']},
                {"id": 33, "value": discogs_data['country']},
                {"id": 31, "value": entry["Project"]},
                {"id": 12, "value": band_members},
                {"id": 19, "value": discogs_data['formats'][0]['descriptions'][1] if len(discogs_data['formats'][0]['descriptions']) > 1 else ""},
                {"id": 37, "value": " ".join(label['name'].replace(" ", "") for label in discogs_data['labels'])},
                {"id": 25, "value": entry["Year Release"]},
                {"id": 4, "value": discogs_data['year']},
                {"id": 15, "value": discogs_data['formats'][0]['descriptions'][0] if discogs_data['formats'][0]['descriptions'] else ""},
                {"id": 17, "value": discogs_data['labels'][0]['catno'] if discogs_data['labels'] else ""},
                {"id": 11, "value": discogs_data.get('notes', '')},
                {"id": 18, "value": discogs_data['formats'][0].get('text', '') if 'formats' in discogs_data else ""},
                {"id": 9, "value": next((identifier['value'] for identifier in discogs_data['identifiers'] if identifier['type'] == 'Barcode'), '')},
                {"id": 8, "value": discogs_data['resource_url']},
                {"id": 28, "value": entry["Quantity"]},
                {"id": 24, "value": entry["Cost"]},
                {"id": 5, "value": entry["Is Autographed"]},
            ]
        }
        self.create_entry(entry_data, photo_path)

# Routes
@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload/<tab>', methods=['POST'])
def upload(tab):
    if tab not in MEMENTODB_LIBRARY_IDS:
        return "Invalid tab", 400

    uploader_class = {
        'vinyls': VinylsUploader,
        'cd': None,  # Placeholder for future implementation
        'books': None,  # Placeholder for future implementation
        'drumsticks': None  # Placeholder for future implementation
    }.get(tab)

    if not uploader_class:
        return "Not implemented yet", 501

    uploader = uploader_class(MEMENTODB_LIBRARY_IDS[tab])
    description = request.form['description']
    photos = request.files.getlist('photos')

    try:
        # Validate JSON and photos
        entries_data = json.loads(description)
        uploader.validate_inputs(entries_data, photos)

        # Ensure description and photos match
        if len(entries_data) != len(photos):
            return "Number of JSON objects must match the number of photos", 400

        # Process entries and photos
        for entry, photo in zip(entries_data, photos):
            photo_path = f"/tmp/{photo.filename}"
            photo.save(photo_path)  # Save photo temporarily
            uploader.process_entry(entry, photo_path)

        flash("Data processed successfully!", "success")
    except (json.JSONDecodeError, ValueError) as e:
        flash(str(e), "danger")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
