### Seed All Data
```bash
python seeds/seed_manager.py seed --all
```

### Seed Specific Data
```bash
# Seed roles only
docker-compose exec app  python seeds/seed_manager.py seed --roles

# Seed role tasks only
docker-compose exec app  python seeds/seed_manager.py seed --role-tasks

# Seed onboarding content only
docker-compose exec app  python seeds/seed_manager.py seed --onboarding-content

# Seed integration content only
docker-compose exec app python seeds/seed_manager.py seed --integration-content
```

### Clear Data
```bash
# Clear all seeded data
python seeds/seed_manager.py clear --all
```

### Check Status
```bash
# Show current seeding status
python seeds/seed_manager.py status
```
