"""
Schedules para o pipeline de captura do BRT
"""
from datetime import timedelta

from prefect.schedules import Schedule
from prefect.schedules.clocks import IntervalClock

from pipelines.constants import Constants


# =========================================================================
# SCHEDULE: Captura Minuto a Minuto
# =========================================================================

# Schedule para captura de dados a cada minuto
brt_minute_schedule = Schedule(
    clocks=[
        IntervalClock(
            interval=timedelta(minutes=Constants.CAPTURE_INTERVAL_MINUTES.value),
            parameter_defaults={
                "api_url": Constants.BRT_API_URL.value,
                "bucket_name": Constants.GCS_BUCKET_NAME.value,
                "gcs_destination_prefix": "bronze/brt_gps",
                "output_dir": "./data",
                "keep_local_file": True,
                "materialize_dbt": False,
                "dataset_id": Constants.BQ_DATASET_RAW.value
            },
            labels=["civitas", "brt", "scheduled"]
        )
    ]
)


# =========================================================================
# SCHEDULE: Captura com Materializao DBT (a cada 10 minutos)
# =========================================================================

# Schedule para captura + materializao DBT a cada 10 minutos
brt_with_dbt_schedule = Schedule(
    clocks=[
        IntervalClock(
            interval=timedelta(minutes=Constants.CSV_GENERATION_MINUTES.value),
            parameter_defaults={
                "api_url": Constants.BRT_API_URL.value,
                "bucket_name": Constants.GCS_BUCKET_NAME.value,
                "gcs_destination_prefix": "bronze/brt_gps",
                "output_dir": "./data",
                "keep_local_file": True,
                "materialize_dbt": True,  # Ativa DBT aps upload
                "dataset_id": Constants.BQ_DATASET_RAW.value
            },
            labels=["civitas", "brt", "scheduled", "dbt"]
        )
    ]
)


# =========================================================================
# SCHEDULE: Desenvolvimento/Testes (a cada 5 minutos)
# =========================================================================

# Schedule para desenvolvimento e testes (mais frequente)
brt_dev_schedule = Schedule(
    clocks=[
        IntervalClock(
            interval=timedelta(minutes=5),
            parameter_defaults={
                "api_url": Constants.BRT_API_URL.value,
                "bucket_name": Constants.GCS_BUCKET_NAME.value,
                "gcs_destination_prefix": "bronze/brt_gps/dev",
                "output_dir": "./data",
                "keep_local_file": True,
                "materialize_dbt": False,
                "dataset_id": Constants.BQ_DATASET_RAW.value
            },
            labels=["civitas", "brt", "development"]
        )
    ]
)


# =========================================================================
# EXPORTAR SCHEDULES
# =========================================================================

__all__ = [
    "brt_minute_schedule",
    "brt_with_dbt_schedule",
    "brt_dev_schedule"
]
