from mangum import Mangum

from app.main import app

# Mangum adapts API Gateway events to ASGI for Lambda.
handler = Mangum(app, lifespan="auto")
