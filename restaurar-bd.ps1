docker compose up -d
Write-Host "Esperando a SQL Server..."
Start-Sleep -Seconds 25
docker cp db/proveedores_db.bak bd-proyecto:/var/opt/mssql/data/
docker exec bd-proyecto /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "TrioPerras2026" -C -Q "RESTORE DATABASE proveedores_db FROM DISK='/var/opt/mssql/data/proveedores_db.bak' WITH MOVE 'proveedores_db' TO '/var/opt/mssql/data/proveedores_db.mdf', MOVE 'proveedores_db_log' TO '/var/opt/mssql/data/proveedores_db_log.ldf', REPLACE"
Write-Host "Listo. Ya puedes abrir la app."