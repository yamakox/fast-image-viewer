from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import env
from app.routers import folders, images

app = FastAPI(title='fast-image-viewer', docs_url='/docs', redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=env.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(folders.router, prefix='/api/v1')
app.include_router(images.router, prefix='/api/v1')
