# MusicCat

A CD catalog application that lets you scan barcodes using your phone camera and retrieves album information from MusicBrainz.

## Features

- Scan CD barcodes using phone camera
- Automatic metadata lookup from MusicBrainz
- Cover art from Cover Art Archive
- Track listings for each album
- Search your collection by album/artist or track name
- Duplicate detection
- SQLite database - no external dependencies

## Prerequisites

- Python 3.x
- For iOS camera access: HTTPS required (use Tailscale or similar)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv .
```

### 2. Activate Virtual Environment

```bash
# Mac/Linux
source bin/activate

# Windows
Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate SSL Certificates (for iOS camera access)

iOS Safari requires HTTPS for camera access. Using Tailscale:

```bash
# Find your Tailscale IP
tailscale ip -4

# Install mkcert
brew install mkcert
mkcert -install
mkcert <your-tailscale-ip>
```

This creates `<filename>.pem` and `<filename>-key.pem` files.

### 5. Run the App

```bash
python app.py
```

## Docker

### Build and Run with Docker Compose

```bash
docker-compose up --build
```

### Build and Run Manually

```bash
# Build the image
docker build -t musiccat .

# Run the container
docker run -p 6123:6123 -v $(pwd)/musiccat.db:/app/musiccat.db -v $(pwd)/cert.pem:/app/cert.pem:ro -v $(pwd)/key.pem:/app/key.pem:ro musiccat
```

### Notes

- The database is persisted via volume mount to `musiccat.db`
- SSL certificates (`cert.pem`, `key.pem`) are mounted read-only
- For iOS camera access, you'll need valid SSL certificates

## Usage

### Access the App

- **Same machine:** http://localhost:6123
- **Via Tailscale:** https://[tailscale-ip]:6123

### Scanning CDs

1. Go to "Scan CD" page
2. Point your phone camera at the barcode
3. Tap "Capture" when the barcode is detected
4. Review and add to collection

### Searching

- Use the search box on the homepage to find albums by title/artist
- Use track search to find albums containing a specific track

### Finding Duplicates

- Click "Duplicates" in the navigation to find duplicate CDs

## Project Structure

```
musiccat/
├── app.py              # Flask application
├── models.py           # Database models
├── api_client.py       # MusicBrainz API client
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── scan.html
│   ├── cd_detail.html
│   └── duplicates.html
└── musiccat.db         # SQLite database (created on first run)
```

## API Endpoints

- `GET /` - Collection view
- `GET /scan` - Barcode scanner
- `GET /cd/<id>` - CD details
- `GET /duplicates` - Find duplicates
- `GET /api/lookup?barcode=<barcode>` - Lookup barcode
- `POST /api/add` - Add CD to collection

## License

MIT
