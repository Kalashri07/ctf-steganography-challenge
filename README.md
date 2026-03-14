# CTF Challenge Web Application

Flask web application for hosting the Hard-Level Steganography CTF Challenge.

## Features

- Challenge description and file download
- Flag submission with validation
- Hint system with point deductions
- Session-based scoring
- Statistics tracking
- Responsive design

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Visit http://localhost:5000
```

## Deploy to Render

See RENDER_DEPLOYMENT_GUIDE.md for complete instructions.

## Configuration

Edit `app.py` to customize:
- Challenge name and description
- Flag value
- Points and hint costs
- Hints text

## Security Notes

- Change SECRET_KEY in production (Render auto-generates)
- Uses session-based storage (consider database for production)
- No authentication (add if needed)

## Challenge File

Place your `challenge.png` in the `static/` directory before deploying.
