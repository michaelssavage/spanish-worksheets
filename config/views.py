import django_rq
from django.http import HttpResponse, JsonResponse
from rq import Worker


def health(request):
    """200 only when Redis is up and at least one RQ worker listens on ``default``."""
    try:
        conn = django_rq.get_connection("default")
        conn.ping()
    except Exception:
        return JsonResponse({"redis": "error", "workers_on_default": 0}, status=503)

    try:
        workers = Worker.all(connection=conn)
    except Exception:
        return JsonResponse({"redis": "ok", "workers_on_default": 0}, status=503)

    on_default = [w for w in workers if "default" in w.queue_names()]
    payload = {
        "redis": "ok",
        "workers_total": len(workers),
        "workers_on_default": len(on_default),
    }
    return JsonResponse(payload, status=200 if on_default else 503)


def home(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Worksheet API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .status { color: #27ae60; font-weight: bold; }
            ul { line-height: 1.8; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Spanish Worksheet API</h1>
            <p class="status">✓ Server is running</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/admin/">/admin/</a> - Django Admin</li>
                <li><strong>/api/docs/</strong> - Swagger UI</li>
                <li><strong>/api/token/</strong> - Get authentication token (POST)</li>
                <li><strong>/api/worksheet/generate-content/</strong> - Generate content only (POST)</li>
                <li><strong>/api/worksheet/generate-worksheet/</strong> - Generate worksheet (POST)</li>
            </ul>
            <h2>Quick Start:</h2>
            <ol>
                <li>Get a token: <code>POST /api/token/</code></li>
                <li>Use token in header: <code>Authorization: Token YOUR_TOKEN</code></li>
                <li>Generate worksheet: <code>POST /api/worksheet/generate-content/</code></li>
            </ol>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
