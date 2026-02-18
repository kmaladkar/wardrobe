# Repository structure

How folders map to the app design in [IDEAS.md](../IDEAS.md).

```
wardrobe/
├── src/wardrobe/              # main package
│   ├── api/                   # §3 Platform – Python backend
│   │   ├── routes/            # REST: auth, users, items, outfits, recommendations
│   │   ├── middleware/
│   │   └── dependencies.py
│   ├── core/                  # §1 Core product
│   │   ├── recommendation/    # Engine, rules (occasion/color/formality), scoring
│   │   └── wardrobe/          # Catalog, history, analytics (virtual closet)
│   ├── ml/                    # §2 AI/ML
│   │   ├── vision/            # Tagging, embeddings
│   │   ├── compatibility/     # Outfit scoring model
│   │   ├── personalization/   # Feedback, style profile
│   │   └── generative/        # Captions, mood/theme prompts
│   ├── data/                  # §4 Data & models
│   │   ├── models/            # Item, Outfit, User schemas
│   │   ├── repositories/      # CRUD, filters
│   │   └── embeddings_store.py
│   ├── services/              # §3 – external & infra
│   │   ├── storage/           # Images (S3), thumbnails
│   │   ├── weather.py
│   │   ├── calendar.py
│   │   └── queue.py           # Background tasks
│   └── config/                # Settings, env
├── tests/                     # api, core, ml
├── scripts/                   # Migrations, seed, training
└── docs/
```

- **§1 Core**: `core/recommendation/`, `core/wardrobe/`
- **§2 AI/ML**: `ml/vision/`, `ml/compatibility/`, `ml/personalization/`, `ml/generative/`
- **§3 Backend**: `api/`, `services/`
- **§4 Data**: `data/models/`, `data/repositories/`, `data/embeddings_store.py`
- **§5 Nice-to-have**: New modules under `core/` or `services/` (e.g. `core/packing/`, `services/wishlist/`) as needed.
