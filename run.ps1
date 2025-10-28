# CIVITAS Data Engineering - Script de Gerenciamento
# Uso: .\run.ps1 <comando>

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$COMPOSE = "docker compose -f docker/docker-compose.yml"
$CLI_SERVICE = "cli"

function Show-Help {
    Write-Host ""
    Write-Host "🚀 CIVITAS Data Engineering - Comandos Disponíveis" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup:" -ForegroundColor Yellow
    Write-Host "  setup           Setup completo (build + up + setup-gcp + validate + register)"
    Write-Host "  build           Build das imagens Docker"
    Write-Host "  up              Sobe Prefect Server + Agent + PostgreSQL"
    Write-Host ""
    Write-Host "Controle:" -ForegroundColor Yellow
    Write-Host "  down            Para todos os serviços"
    Write-Host "  restart         Reinicia serviços"
    Write-Host "  logs            Mostra logs em tempo real"
    Write-Host "  shell           Abre shell no container CLI"
    Write-Host ""
    Write-Host "Scripts:" -ForegroundColor Yellow
    Write-Host "  test            Testa API do BRT"
    Write-Host "  validate        Valida ambiente completo"
    Write-Host "  register        Registra flows no Prefect"
    Write-Host ""
    Write-Host "GCP:" -ForegroundColor Yellow
    Write-Host "  setup-gcp       Cria recursos no GCP (bucket + datasets)"
    Write-Host "  gcloud <args>   Executa comando gcloud"
    Write-Host "  gsutil <args>   Executa comando gsutil"
    Write-Host "  bq <args>       Executa comando bq"
    Write-Host "  dbt <args>      Executa comando dbt"
    Write-Host ""
    Write-Host "Limpeza:" -ForegroundColor Yellow
    Write-Host "  clean           Remove containers, volumes e imagens"
    Write-Host ""
    Write-Host "Exemplos:" -ForegroundColor Green
    Write-Host "  .\run.ps1 setup            # Setup completo"
    Write-Host "  .\run.ps1 up               # Apenas subir serviços"
    Write-Host "  .\run.ps1 gcloud auth list # Listar contas autenticadas"
    Write-Host "  .\run.ps1 dbt debug        # Testar conexão DBT"
    Write-Host ""
}

function Invoke-Build {
    Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE build"
}

function Invoke-Up {
    Write-Host "🚀 Starting services..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE up -d postgres prefect-server prefect-agent"
    Write-Host ""
    Write-Host "✅ Serviços iniciados!" -ForegroundColor Green
    Write-Host "   Prefect UI: http://localhost:8080" -ForegroundColor White
    Write-Host "   Prefect API: http://localhost:4200" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   .\run.ps1 setup-gcp    # Criar recursos no GCP"
    Write-Host "   .\run.ps1 validate     # Validar ambiente"
    Write-Host "   .\run.ps1 register     # Registrar flows"
    Write-Host ""
}

function Invoke-Down {
    Write-Host "⏹️  Stopping services..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE down"
}

function Invoke-Restart {
    Write-Host "🔄 Restarting services..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE restart"
}

function Invoke-Logs {
    Write-Host "📋 Showing logs (Ctrl+C to exit)..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE logs -f"
}

function Invoke-Shell {
    Write-Host "🐚 Opening shell in CLI container..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE /bin/bash"
}

function Invoke-Test {
    Write-Host "🧪 Testing BRT API..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE scripts/test_brt_api.py"
}

function Invoke-Validate {
    Write-Host "✅ Validating environment..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE scripts/validate_environment.py"
}

function Invoke-Register {
    Write-Host "📝 Registering flows..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE scripts/register_flows.py"
}

function Invoke-SetupGCP {
    Write-Host "🔧 Creating GCP resources..." -ForegroundColor Cyan
    Write-Host ""
    
    $script = @"
set -e
echo '📦 Verificando projeto...'
gcloud config get-value project || echo 'Projeto não configurado'
echo ''
echo '🪣 Criando bucket GCS...'
gsutil mb -l us-east1 gs://civitas-brt-data || echo 'Bucket já existe'
echo ''
echo '📊 Criando datasets BigQuery...'
bq mk --dataset --location=us-east1 civitas-data-eng:brt_raw || echo 'Dataset brt_raw já existe'
bq mk --dataset --location=us-east1 civitas-data-eng:brt_staging || echo 'Dataset brt_staging já existe'
bq mk --dataset --location=us-east1 civitas-data-eng:brt_gold || echo 'Dataset brt_gold já existe'
echo ''
echo '✅ Recursos GCP criados/verificados!'
"@
    
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE /bin/bash -c `"$script`""
}

function Invoke-GCloud {
    $gcloudArgs = $Args -join " "
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE gcloud $gcloudArgs"
}

function Invoke-GSUtil {
    $gsutilArgs = $Args -join " "
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE gsutil $gsutilArgs"
}

function Invoke-BQ {
    $bqArgs = $Args -join " "
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE bq $bqArgs"
}

function Invoke-DBT {
    $dbtArgs = $Args -join " "
    Invoke-Expression "$COMPOSE run --rm $CLI_SERVICE dbt --project-dir queries $dbtArgs"
}

function Invoke-Clean {
    Write-Host "🧹 Cleaning up..." -ForegroundColor Cyan
    Invoke-Expression "$COMPOSE down -v --remove-orphans"
    docker rmi civitas-data-eng-cli civitas-data-eng-prefect-agent 2>$null
}

function Invoke-Setup {
    Write-Host "🎬 Full setup starting..." -ForegroundColor Cyan
    Write-Host ""
    Invoke-Build
    Invoke-Up
    Start-Sleep -Seconds 5
    Invoke-SetupGCP
    Invoke-Validate
    Invoke-Register
    Write-Host ""
    Write-Host "🎉 Setup completo!" -ForegroundColor Green
    Write-Host "   Acesse: http://localhost:8080" -ForegroundColor White
    Write-Host ""
}

# Executar comando
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "build" { Invoke-Build }
    "up" { Invoke-Up }
    "down" { Invoke-Down }
    "restart" { Invoke-Restart }
    "logs" { Invoke-Logs }
    "shell" { Invoke-Shell }
    "test" { Invoke-Test }
    "validate" { Invoke-Validate }
    "register" { Invoke-Register }
    "setup-gcp" { Invoke-SetupGCP }
    "gcloud" { Invoke-GCloud }
    "gsutil" { Invoke-GSUtil }
    "bq" { Invoke-BQ }
    "dbt" { Invoke-DBT }
    "clean" { Invoke-Clean }
    "setup" { Invoke-Setup }
    default {
        Write-Host "❌ Comando desconhecido: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
