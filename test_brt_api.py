"""
Script para testar a captura da API do BRT localmente

Uso:
    python test_brt_api.py
"""
import requests
import json
from datetime import datetime


def test_brt_api():
    """
    Testa a API do BRT e mostra estrutura dos dados.
    """
    api_url = "https://dados.mobilidade.rio/gps/brt"
    
    print("=" * 70)
    print("🧪 TESTE DA API DO BRT")
    print("=" * 70)
    print(f"📡 URL: {api_url}")
    print("")
    
    try:
        print("⏳ Fazendo requisição...")
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Tempo de resposta: {response.elapsed.total_seconds():.2f}s")
        print("")
        
        # Parse JSON
        data = response.json()
        
        print("📊 ESTRUTURA DOS DADOS:")
        print("-" * 70)
        print(f"Tipo: {type(data)}")
        
        if isinstance(data, list):
            print(f"Total de registros: {len(data)}")
            print("")
            
            if len(data) > 0:
                print("🔍 Exemplo do primeiro registro:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
                print("")
                
                print("📋 Campos disponíveis:")
                for key in data[0].keys():
                    value = data[0][key]
                    print(f"  • {key}: {type(value).__name__} = {value}")
        else:
            print("⚠️ Formato inesperado (não é lista)")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        print("")
        print("=" * 70)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        
        return data
        
    except requests.RequestException as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return None


if __name__ == "__main__":
    test_brt_api()
