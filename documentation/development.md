# Development Commands

## Quick Start
```bash
# Start all containers
docker-compose up -d

# Frontend: https://stinercut.local (via Traefik)
# Backend API: https://api.stinercut.local (via Traefik)
# Backend direct: http://localhost:8002
```

## Docker
```bash
docker-compose up -d              # Start services
docker-compose logs -f backend    # View backend logs
docker-compose restart backend    # Restart backend
docker-compose down -v            # Stop and remove volumes
```

## Frontend
```bash
docker-compose exec frontend bash
composer install                  # Install PHP deps
php bin/console eloquent:migrate  # Run migrations
php bin/console cache:clear       # Clear cache
npm run dev                       # Build assets
npm run watch                     # Watch mode
```

## Backend
```bash
docker-compose exec backend bash
pip install -r requirements.txt   # Install Python deps
```

## Database
```bash
docker-compose exec -T mysql mysql -u stiner -plocal stinercut
```

## OpenSpec Workflow
```bash
openspec list                     # List active changes
openspec list --specs             # List specifications
openspec show <change-id>         # View change details
openspec validate <id> --strict   # Validate change
openspec archive <id> --yes       # Archive completed change
```
