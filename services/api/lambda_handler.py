from mangum import Mangum
from app.main import app

# Mangum handler for AWS Lambda
handler = Mangum(app)
