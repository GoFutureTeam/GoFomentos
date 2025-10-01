# Script para iniciar a aplicação com Docker Compose

Write-Host "Iniciando os serviços do GoFomentos..." -ForegroundColor Green

# Verificar se o arquivo .env existe
if (-not (Test-Path -Path "./backend/.env")) {
    Write-Host "Arquivo .env não encontrado. Copiando de .env.example..." -ForegroundColor Yellow
    Copy-Item -Path "./backend/.env.example" -Destination "./backend/.env"
    Write-Host "Arquivo .env criado. Por favor, edite-o com suas configurações antes de continuar." -ForegroundColor Yellow
    exit
}

# Iniciar os serviços com Docker Compose
docker-compose up -d

# Verificar se os serviços estão rodando
$services = docker-compose ps
if ($services -match "Up") {
    Write-Host "Serviços iniciados com sucesso!" -ForegroundColor Green
    Write-Host "API disponível em: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Documentação da API: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "MongoDB disponível em: localhost:27017" -ForegroundColor Cyan
    Write-Host "ChromaDB disponível em: http://localhost:8001" -ForegroundColor Cyan
} else {
    Write-Host "Erro ao iniciar os serviços. Verifique os logs com 'docker-compose logs'." -ForegroundColor Red
}
