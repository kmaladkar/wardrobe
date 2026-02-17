# Wardrobe – Ideas & Roadmap

Ideas and features we can develop for the Generative AI outfit recommendation mobile app (Python backend + mobile client).

---

## 1. Core product

### Outfit recommendation engine
- **Outfit generation from wardrobe**: Given a set of clothing items (photos + metadata), recommend full outfits (top + bottom + shoes + accessories).
- **Occasion-based recommendations**: “Work”, “Date”, “Casual”, “Formal”, “Sport”, “Travel” with different style rules.
- **Weather-aware suggestions**: Use location/forecast to suggest layers, coats, and fabrics.
- **“What to wear today”**: One-tap daily suggestion based on calendar, weather, and occasion.
- **Outfit scoring**: Rate how well items go together (color, formality, style) and surface best combinations.

### Wardrobe as a collection
- **Catalog your clothes**: Upload photos of each item; tag category (top, bottom, shoes, etc.), color, pattern, formality, season.
- **Outfit history**: Log “worn” outfits and dates to avoid repetition and balance rotation.
- **Virtual closet**: Browse and filter your collection (e.g. “all blue tops”, “formal shoes”).
- **Wardrobe analytics**: Most/least worn items, color distribution, gaps (e.g. “no neutral blazer”).

---

## 2. AI / ML features

### Vision & understanding
- **Auto-tagging from photos**: Use vision models to detect category, color, pattern, neckline, sleeve length, etc.
- **Style and aesthetic labels**: “Minimalist”, “Preppy”, “Streetwear”, “Bohemian” from image + metadata.
- **Outfit compatibility model**: Train or fine-tune a model to score (item, item) or (outfit) compatibility.
- **Virtual try-on (future)**: Generate images of “you” wearing a suggested outfit (advanced generative models).

### Personalization
- **Learn from feedback**: Like/dislike or “wore it” signals to improve future recommendations.
- **Style profile**: Quiz or implicit signals (saved outfits, likes) to build a style vector.
- **Body shape / fit preferences**: Optional inputs to bias toward certain cuts or silhouettes.

### Generative ideas
- **“Complete the outfit”**: User selects one or two items; model suggests the rest from the closet.
- **“What else could I wear with this?”**: For a chosen item, list alternative pairings.
- **Mood/theme prompts**: “Something bold today” or “Cozy and casual” to steer generation.
- **Caption generation**: Short, shareable captions for outfits (e.g. for social).

---

## 3. Platform & experience

### Mobile app (client)
- **Native or cross-platform**: React Native, Flutter, or native (Swift/Kotlin) calling a Python API.
- **Camera-first**: Quick photo capture and crop for adding items.
- **Swipe / card UI**: Tinder-style “like/dislike” for outfit suggestions to collect feedback.
- **Calendar integration**: Optional link to calendar events for occasion-aware “what to wear”.
- **Offline mode**: Cache recent outfits and wardrobe so basics work without network.

### Python backend
- **REST or GraphQL API**: Auth, wardrobe CRUD, recommendation endpoints.
- **Async and scalable**: FastAPI + background jobs for ML inference and embedding.
- **Image storage**: S3-compatible or similar for item photos; thumbnails and CDN.
- **Queue for heavy tasks**: Celery, RQ, or task queue for outfit generation and model runs.

---

## 4. Data & models

### Data layer
- **Items schema**: id, user_id, image_url(s), category, subcategory, colors, pattern, formality, season, brand, purchase_date, etc.
- **Outfits schema**: id, user_id, item_ids[], occasion, date_worn, rating, weather (optional).
- **Embeddings**: Store vector embeddings per item (and optionally per outfit) for similarity and retrieval.

### Model choices (Python)
- **Vision**: CLIP, ResNet, or dedicated fashion models (e.g. from Hugging Face) for tagging and embeddings.
- **Compatibility / scoring**: Small classifier or ranker trained on (outfit, label) or (item pair, score).
- **Recommendation**: Retrieval (e.g. vector search) + reranking; optional sequence model for “next item” in an outfit.
- **LLMs**: Optional for natural-language queries (“something that works for a job interview”) and captions.

---

## 5. Nice-to-have features

- **Wishlist / shopping**: “You don’t have a navy blazer – here are options” with affiliate or product links.
- **Outfit sharing**: Share outfit cards (image + items) with friends or to social.
- **Packing lists**: Generate “what to pack” for a trip from wardrobe and trip length/occasion.
- **Laundry / care**: Remind “not worn in 30 days” or “dry-clean” by item.
- **Sustainability**: “Wear count”, “cost per wear”, and nudges to reuse and repair.
- **Multi-user / household**: Shared closet (e.g. family) with filters by person.
- **AR try-on**: Overlay clothing on user’s photo (harder; can start as later phase).

---

## 6. Technical roadmap (high level)

1. **Repo & API**: Python project with uv (done); add FastAPI, auth, and basic CRUD for users and items.
2. **Wardrobe ingestion**: Upload images; store metadata; optional vision pipeline for auto-tags.
3. **Simple rules engine**: Outfit suggestions from rules (e.g. color harmony, formality match) before ML.
4. **Embeddings & retrieval**: Embed items; “complete the outfit” via similarity and filters.
5. **Compatibility / ranking model**: Train or plug a model to score full outfits; integrate into API.
6. **Mobile client**: Build app (React Native / Flutter / native) against the API; camera and basic UI.
7. **Personalization**: Feedback loop and style profile; A/B tests on recommendation quality.
8. **Polish**: Weather, calendar, history, and one-tap “what to wear today”.

---

## 7. Open questions

- **Mobile stack**: Pure Python (e.g. Kivy, BeeWare) vs separate mobile app + Python backend?
- **Hosting**: Where to run Python (Railway, Fly.io, AWS, GCP) and where to run inference (CPU vs GPU)?
- **First launch**: Start with “catalog + rule-based suggestions” or invest in ML from day one?
- **Data source**: Only user-uploaded photos, or also scrape/catalog for “discovery” and wishlist?

Use this doc to pick the next slice to build and to keep the big picture in mind.
