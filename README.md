
# Item Storing Project

The **Item Storing Project** is a dynamic web application designed to organize and preserve collections using MementoDB. It integrates with third-party APIs like Discogs to fetch supplementary information and seamlessly upload data entries. This project is tailored for managing Vinyls and is scalable to include other collection types such as CDs, books, and drumsticks (currently under development). The application ensures efficient, structured, and user-friendly data management.

## Features

- Integration with MementoDB for data storage.
- Fetching detailed metadata from Discogs API for Vinyl and CD entries.
- Uploading entries with associated photos for complete documentation.
- Dynamic and modular architecture, enabling future expansion for CDs, books, and drumsticks.

---

## Installation Guide

### Step 1: Install Poetry
Poetry is used for managing dependencies and virtual environments. Install Poetry using `pipx`:

```bash
pipx install poetry
```

### Step 2: Clone the Repository
Clone this repository to your local system:

```bash
git clone https://github.com/your-repository/item-storing-project.git
cd item-storing-project
```

### Step 3: Install Dependencies
Run the following command to install the required dependencies using Poetry:

```bash
poetry add flask requests python-dotenv
```

### Step 4: Run the Application
Start the Flask server using Poetry:

```bash
poetry run flask --app upload_entries.app run
```

The application will be available at `http://127.0.0.1:5000`.

---

## Environment Variables

The project uses a `.env` file to store sensitive information like API keys and library IDs. Create a `.env` file in the project root directory and add the following variables:

```dotenv
FLASK_SECRET_KEY=your-secret-key
MEMENTODB_API_KEY=your-mementodb-api-key
MEMENTODB_LIBRARY_IDS={"vinyls": "your-vinyls-library-id", "cds": "", "books": "", "drumsticks": ""}
DISCOGS_USER_TOKEN=your-discogs-user-token
```

### Important
- Add `.env` to your `.gitignore` file to ensure that sensitive information is not pushed to version control.

---

## Test File Structure

The test file structure is a JSON file used for uploading Vinyl entries. Each object in the JSON array represents an entry with detailed metadata. Below is an example:

```json
[
    {
        "ReleaseId": 13628752,
        "Sleeve Condition": "Near Mint",
        "Media Condition": "Mint",
        "Family": "Vinyl Classics",
        "Project": "Main",
        "Year Release": "2020",
        "Quantity": 1,
        "Cost": "25.00",
        "Is Autographed": "False"
    },
    {
        "ReleaseId": 27163644,
        "Sleeve Condition": "Very Good Plus",
        "Media Condition": "Very Good",
        "Family": "Rare Finds",
        "Project": "Main",
        "Year Release": "2019",
        "Quantity": 2,
        "Cost": "30.00",
        "Is Autographed": "True"
    }
]
```

### Fields Description

- **ReleaseId**: Discogs release ID for fetching metadata.
- **Sleeve Condition**: Physical condition of the sleeve (e.g., "Near Mint").
- **Media Condition**: Physical condition of the media (e.g., "Mint").
- **Family**: Category or collection group (e.g., "Vinyl Classics").
- **Project**: Project name associated with the entry (e.g., "Main").
- **Year Release**: Year the item was released.
- **Quantity**: Number of items being uploaded.
- **Cost**: Cost of the item.
- **Is Autographed**: Indicates if the item is autographed (`"True"` or `"False"`).

---

## Future Plans

- Add support for CDs, books, and drumsticks.
- Enhance the UI for better user experience.
- Implement advanced validation for entries and photos.
