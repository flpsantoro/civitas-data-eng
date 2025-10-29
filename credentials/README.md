# 🔐 Credenciais GCP# Credenciais GCP



## Para Avaliadores do Desafio CIVITAS## Service Account Configurada



Por questões de segurança, as credenciais não estão commitadas no repositório público.- **Email**: `civitas@civitas-data-eng.iam.gserviceaccount.com`

- **Project**: `civitas-data-eng`

### Opção 1: Usar Credenciais Fornecidas (Recomendado)- **Arquivo**: `civitas-data-eng-8feab1c31a9a.json`



**Entre em contato com o autor** para receber o arquivo:## Permissões Necessárias

- **Email/Slack**: Solicitar `civitas-data-eng-8feab1c31a9a.json`

- **Copiar para**: `credentials/civitas-data-eng-8feab1c31a9a.json`Para o pipeline funcionar, a service account precisa das seguintes roles no GCP:



### Opção 2: Criar Própria Service Account### BigQuery

- `roles/bigquery.dataEditor` - Criar e modificar tabelas

1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts- `roles/bigquery.jobUser` - Executar queries



2. Crie um projeto GCP (ou use existente)**OU**



3. Crie uma Service Account com as seguintes permissões:- `roles/bigquery.admin` - Acesso completo

   - `BigQuery Data Editor`

   - `BigQuery Job User`### Cloud Storage

   - `Storage Object Admin`- `roles/storage.objectAdmin` - Upload e leitura de arquivos



4. Gere chave JSON e salve como: `credentials/civitas-data-eng-YOUR_PROJECT.json`**OU**



5. Atualize o `.env`:- `roles/storage.admin` - Acesso completo

   ```bash

   GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/civitas-data-eng-YOUR_PROJECT.json## Validar Permissões

   GCP_PROJECT_ID=YOUR_PROJECT_ID

   GCS_BUCKET_NAME=YOUR_BUCKET_NAME```bash

   ```# Listar roles da service account

gcloud projects get-iam-policy civitas-data-eng \

### Estrutura Esperada  --flatten="bindings[].members" \

  --filter="bindings.members:serviceAccount:civitas@civitas-data-eng.iam.gserviceaccount.com" \

```  --format="table(bindings.role)"

credentials/```

├── README.md (este arquivo)

└── civitas-data-eng-*.json (arquivo de credenciais - não commitado)## Adicionar Permissões (se necessário)

```

```bash

### Validar Credenciais# BigQuery

gcloud projects add-iam-policy-binding civitas-data-eng \

```bash  --member="serviceAccount:civitas@civitas-data-eng.iam.gserviceaccount.com" \

# No container  --role="roles/bigquery.dataEditor"

docker exec civitas-prefect-agent python -c "from google.cloud import bigquery; print('✅ Credencial válida!', bigquery.Client().project)"

```gcloud projects add-iam-policy-binding civitas-data-eng \

  --member="serviceAccount:civitas@civitas-data-eng.iam.gserviceaccount.com" \

---  --role="roles/bigquery.jobUser"



**⚠️ IMPORTANTE**: Nunca commite credenciais GCP em repositórios públicos!# Cloud Storage

gcloud projects add-iam-policy-binding civitas-data-eng \
  --member="serviceAccount:civitas@civitas-data-eng.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```
