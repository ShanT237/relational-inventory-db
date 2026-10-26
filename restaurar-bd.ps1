$ErrorActionPreference = "Stop"

# La clave de "sa" se lee del archivo .env (no va escrita en el script).
if (-not (Test-Path ".env")) {
    Write-Host "Error: falta el archivo .env. Copia .env.example como .env y define MSSQL_SA_PASSWORD." -ForegroundColor Red
    exit 1
}
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
        Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2]
    }
}
if (-not $env:MSSQL_SA_PASSWORD) {
    Write-Host "Error: MSSQL_SA_PASSWORD esta vacia en .env." -ForegroundColor Red
    exit 1
}

docker compose up -d
if ($LASTEXITCODE -ne 0) { Write-Host "Error: no se pudo iniciar el contenedor." -ForegroundColor Red; exit 1 }

Write-Host "Esperando a SQL Server..."
Start-Sleep -Seconds 25

docker cp db/proveedores_db.bak bd-proyecto:/var/opt/mssql/data/
if ($LASTEXITCODE -ne 0) { Write-Host "Error: no se pudo copiar el respaldo." -ForegroundColor Red; exit 1 }

docker exec bd-proyecto /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $env:MSSQL_SA_PASSWORD -C -Q "RESTORE DATABASE proveedores_db FROM DISK='/var/opt/mssql/data/proveedores_db.bak' WITH MOVE 'proveedores_db' TO '/var/opt/mssql/data/proveedores_db.mdf', MOVE 'proveedores_db_log' TO '/var/opt/mssql/data/proveedores_db_log.ldf', REPLACE"
if ($LASTEXITCODE -ne 0) { Write-Host "Error: fallo la restauracion de la BD." -ForegroundColor Red; exit 1 }

Write-Host "Listo. Ya puedes abrir la app." -ForegroundColor Green
