$ErrorActionPreference = "Stop"

docker compose up -d
if ($LASTEXITCODE -ne 0) { Write-Host "Error: no se pudo iniciar el contenedor." -ForegroundColor Red; exit 1 }

Write-Host "Esperando a SQL Server..."
Start-Sleep -Seconds 25

docker cp db/proveedores_db.bak bd-proyecto:/var/opt/mssql/data/
if ($LASTEXITCODE -ne 0) { Write-Host "Error: no se pudo copiar el respaldo." -ForegroundColor Red; exit 1 }

docker exec bd-proyecto /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "TrioPerras2026" -C -Q "RESTORE DATABASE proveedores_db FROM DISK='/var/opt/mssql/data/proveedores_db.bak' WITH MOVE 'proveedores_db' TO '/var/opt/mssql/data/proveedores_db.mdf', MOVE 'proveedores_db_log' TO '/var/opt/mssql/data/proveedores_db_log.ldf', REPLACE"
if ($LASTEXITCODE -ne 0) { Write-Host "Error: fallo la restauracion de la BD." -ForegroundColor Red; exit 1 }

Write-Host "Listo. Ya puedes abrir la app." -ForegroundColor Green