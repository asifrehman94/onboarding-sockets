## 📁 Structure

```
seeds/
├── data/                    # JSON data files
│   ├── roles.json          # Role definitions
│   ├── role_tasks.json     # Tasks for each role
│   └── onboarding_content.json  # Onboarding content
├── seeders/                # Seeder classes
│   ├── base_seeder.py      # Base seeder functionality
│   ├── role_seeder.py      # Role seeding logic
│   └── role_tasks_seeder.py # Role tasks seeding logic
├── seed_manager.py         # Command-line interface
└── README.md              # This file
```

## 🚀 Usage

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
