import os

import uvicorn

uvicorn.run(
    "grandmas_bouncer.web.app:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000"))
)
