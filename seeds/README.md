### Seed All Data
```bash
python seeds/seed_manager.py seed --all
```

### Seed Specific Data
```bash
# Seed roles only
python seeds/seed_manager.py seed --roles

# Seed role tasks only
python seeds/seed_manager.py seed --role-tasks

# Seed onboarding content only
python seeds/seed_manager.py seed --onboarding-content
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
