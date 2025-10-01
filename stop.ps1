# Script para parar a aplicação com Docker Compose

Write-Host "Parando os serviços do GoFomentos..." -ForegroundColor Yellow

# Parar os serviços com Docker Compose
docker-compose down

Write-Host "Serviços parados com sucesso!" -ForegroundColor Green
