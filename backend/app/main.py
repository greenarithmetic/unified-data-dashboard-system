"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from app.config import settings
from app.database import init_db
from app.api import data, ingest, health, test, superset
from app.services.data_loader import DataLoaderService
from app.database import SessionLocal
from loguru import logger

# Configure logging
logger.add("logs/app.log", rotation="500 MB", retention="10 days", level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Starting Unified Data Dashboard System")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Start scheduler
    scheduler = BackgroundScheduler()
    
    # Add sync job if Google Sheets credentials are configured
    if settings.google_sheets_credentials:
        from app.services.data_loader import DataLoaderService
        
        def sync_datasets():
            """Sync all datasets from Google Sheets"""
            try:
                db = SessionLocal()
                loader = DataLoaderService(db)
                
                # TODO: Load dataset configurations from file/database
                # For now, sync only community_requests
                from app.schemas.dataset_config import (
                    DatasetConfigSchema, FieldConfig, FieldType,
                    DeduplicationConfig, QualityFiltersConfig, IndexesConfig,
                    DeduplicationStrategy
                )
                
                dataset_config = DatasetConfigSchema(
                    id="community_requests",
                    name="Обращения граждан",
                    description="Сбор обращений из чатов",
                    source="google_sheets",
                    sheet_id="1v1aXMDfc9gruLnmJBlVVxRO7Ahila87j9lzEA5Zcj2E",
                    sheet_name="Лист1",
                    sync_interval_minutes=60,
                    schema={
                        "тема": FieldConfig(
                            type=FieldType.TEXT,
                            display_name="Тема обращения",
                            filterable=True,
                            required=True
                        ),
                        "дата": FieldConfig(
                            type=FieldType.DATETIME,
                            display_name="Дата обращения",
                            sortable=True,
                            filterable=True,
                            required=True
                        ),
                        "от_кого": FieldConfig(
                            type=FieldType.TEXT,
                            display_name="От кого",
                            filterable=True,
                            required=True
                        ),
                        "текст": FieldConfig(
                            type=FieldType.TEXT,
                            display_name="Текст обращения",
                            searchable=True,
                            truncate_on_display=150,
                            required=True
                        ),
                        "адрес": FieldConfig(
                            type=FieldType.TEXT,
                            display_name="Адрес",
                            filterable=True,
                            searchable=True
                        ),
                        "ответ": FieldConfig(
                            type=FieldType.BOOLEAN,
                            display_name="Есть ответ",
                            filterable=True
                        )
                    },
                    deduplication=DeduplicationConfig(
                        enabled=True,
                        strategy=DeduplicationStrategy.SOURCE_ID_OR_HASH,
                        unique_fields=["тема", "от_кого", "дата"],
                        hash_algorithm="md5",
                        ttl_days=90
                    ),
                    quality_filters=QualityFiltersConfig(
                        enabled=True,
                        min_text_length=5,
                        max_text_length=10000,
                        spam_keywords=[
                            "спам", "тест", "удалить", "реклама", 
                            "куплю", "продам", "меняю", "дарю"
                        ],
                        spam_patterns=[
                            "^[A-Z0-9]{20,}$",
                            "^http[s]?://",
                            "^[0-9]{20,}$"
                        ],
                        exclude_if_empty=["тема", "от_кого"],
                        exclude_if_contains_only_numbers=True,
                        exclude_if_contains_only_urls=True
                    ),
                    indexes=IndexesConfig(
                        full_text=["текст", "адрес"],
                        bloom_filter=["source_id"],
                        regular=["дата", "тема", "адрес", "от_кого"],
                        composite=[["тема", "дата"], ["адрес", "дата"]]
                    )
                )
                
                result = loader.sync_dataset(dataset_config)
                logger.info(f"Synced dataset: {result}")
                
                db.close()
                
            except Exception as e:
                logger.error(f"Error syncing datasets: {e}")
        
        # Schedule sync job
        scheduler.add_job(
            sync_datasets,
            trigger=IntervalTrigger(minutes=settings.default_sync_interval_minutes),
            id="sync_datasets",
            name="Sync datasets from Google Sheets",
            replace_existing=True
        )
        logger.info(f"Scheduled sync job every {settings.default_sync_interval_minutes} minutes")
    
    scheduler.start()
    
    # Register shutdown handler
    atexit.register(lambda: scheduler.shutdown())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Unified Data Dashboard System")
    scheduler.shutdown()


# Create FastAPI app
app = FastAPI(
    title="Unified Data Dashboard System",
    description="Система дашбордов для анализа данных из Google Sheets",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    data.router,
    prefix=f"{settings.api_v1_str}/data",
    tags=["data"]
)

app.include_router(
    ingest.router,
    prefix=f"{settings.api_v1_str}/ingest",
    tags=["ingest"]
)

app.include_router(
    health.router,
    prefix=f"{settings.api_v1_str}",
    tags=["health"]
)

app.include_router(
    test.router,
    prefix=f"{settings.api_v1_str}/test",
    tags=["test"]
)

app.include_router(
    superset.router,
    prefix=f"{settings.api_v1_str}",
    tags=["superset"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified Data Dashboard System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.api_v1_str}/health"
    }


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    """Redirect to Swagger UI"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")