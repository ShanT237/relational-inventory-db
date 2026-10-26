/* =====================================================================
   02_datos_iniciales.sql  -  Datos que la aplicación necesita para funcionar:
   los 3 roles y los tipos de documento. NO incluye al Administrador: se crea
   con  python src/crear_admin.py  (así su clave no queda escrita en el repositorio).

   Uso:
     sqlcmd -S 127.0.0.1,1433 -U sa -C -d proveedores_db -b -i sql/02_datos_iniciales.sql

   Se puede ejecutar varias veces: solo inserta lo que falta.
   ===================================================================== */
SET NOCOUNT ON;
GO

INSERT INTO dbo.rol (nombre, descripcion)
SELECT v.nombre, v.descripcion
FROM (VALUES
    ('Administrador', N'Único usuario con todos los permisos: crea usuarios y consulta la bitácora'),
    ('Tradicional',   N'Registra, consulta, modifica y elimina datos, y genera reportes'),
    ('Esporadico',    N'Solo realiza consultas')
) AS v (nombre, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM dbo.rol r WHERE r.nombre = v.nombre);
GO

INSERT INTO dbo.tipo_documento (nombre, descripcion)
SELECT v.nombre, v.descripcion
FROM (VALUES
    ('Cedula de ciudadania', N'Documento de identidad de los ciudadanos colombianos mayores de edad'),
    ('Cedula de extranjeria', N'Documento de identidad de los extranjeros residentes en Colombia'),
    ('Pasaporte',            N'Documento de identidad para viajes internacionales')
) AS v (nombre, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM dbo.tipo_documento t WHERE t.nombre = v.nombre);
GO
