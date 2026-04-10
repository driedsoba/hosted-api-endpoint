from mangum import Mangum

from app.main import app

# Mangum translates API Gateway events into ASGI requests,
# allowing the same FastAPI app to run on both Lambda and locally via uvicorn.
handler = Mangum(app, lifespan="auto")
