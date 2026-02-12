# Simple JunoBench Docker Environment Build

## Setup:

```bash
cd docker
docker-compose build --no-cache --pull
docker-compose up
```

## What's Included:
- **Python 3.10** with ALL packages from requirements.txt
- **Jupyter Lab** with no password required
- **All your project files** available in the container

## Files:
- `docker/Dockerfile` - Complete environment with all packages  
- `docker/docker-compose.yml` - Easy startup configuration
- `docker/.dockerignore` - Build optimization

That's it! 🚀