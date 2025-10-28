"""
Script para testar upload manual para GCS
"""
import os
from google.cloud import storage

# Configuração
bucket_name = "civitas-brt-data"
local_file = "/app/data/brt_gps_20251028_145831.csv"
destination_blob = "bronze/brt_gps/test_upload.csv"

print(f"🔧 Testando upload para GCS...")
print(f"   Bucket: {bucket_name}")
print(f"   Arquivo local: {local_file}")
print(f"   Destino: {destination_blob}")
print()

try:
    # Verificar credenciais
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    print(f"✅ Credenciais: {creds}")
    
    # Inicializar cliente
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    # Upload
    print(f"📤 Fazendo upload...")
    blob.upload_from_filename(local_file)
    
    print(f"✅ Upload concluído!")
    print(f"   URI: gs://{bucket_name}/{destination_blob}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
