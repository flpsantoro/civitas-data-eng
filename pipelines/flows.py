"""
Registro central de todos os flows do projeto
Importar este arquivo registra todos os flows automaticamente
"""

# Importar flows
from pipelines.brt.extract_load.flows import brt_extract_load_flow

# Lista de todos os flows disponíveis
ALL_FLOWS = [
    brt_extract_load_flow,
]

__all__ = ["ALL_FLOWS", "brt_extract_load_flow"]
