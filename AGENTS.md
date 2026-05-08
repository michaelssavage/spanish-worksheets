# AGENTS.md

Tests, runserver, and all django commands are run using poetry.

- **Backend API:** `poetry run python manage.py runserver` (never raw `python`/`pip`)
- **Error handling:** catch specific exceptions; log with context before re-raising; prefer early returns
- **Views:** prefer specific DRF generic views (`ListAPIView`, `CreateAPIView`, etc.) over `APIView`; name backoffice views `BackofficeFooListView` / `BackofficeFooDetailView`
- **Serializers:** shape and map all response fields in serializers; views should only query and delegate
- **Queries:** use `select_related`/`prefetch_related` in `get_queryset()` to avoid N+1s