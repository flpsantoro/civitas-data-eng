"""
Script para testar o flow BRT completo com upload para GCS
"""
from pipelines.flows import brt_extract_load_flow

print("\n" + "="*70)
print("🚀 TESTANDO FLOW BRT COMPLETO COM GCS")
print("="*70 + "\n")

result = brt_extract_load_flow.run(
    parameters={
        'keep_local_file': True,
        'materialize_dbt': False
    }
)

print("\n" + "="*70)
if result.is_successful():
    print("✅ FLOW EXECUTADO COM SUCESSO!")
else:
    print("❌ FLOW FALHOU!")
    print(f"Mensagem: {result.message}")
print("="*70 + "\n")

# Exit code
exit(0 if result.is_successful() else 1)
