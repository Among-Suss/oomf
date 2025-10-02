# oomf

"Out of music, fuck!"

Yet another discord music bot in Python

## How to run
Requires `python3` and `ffmpeg`

Create a `.env` file in project folder with the following variables modified accordingly.
```sh
DISCORD_TOKEN=YOUR_TOKEN
DISCORD_PREFIX=BOT_PREFIX
DEBUG_CHANNEL=CHANNEL_ID # Optional, for debug messages
```

In the project folder,
```
pip install -r requirements.txt
cd src
python3 main.py
```
### Using Docker

```sh
 docker run -d --name oomf -e DISCORD_TOKEN="YOUR_TOKEN" -e DISCORD_PREFIX="BOT_PREFIX" poohcom1/oomf:latest
```

## Contributing

### Deployment

Push to `main` branch to deploy to Docker Hub.
