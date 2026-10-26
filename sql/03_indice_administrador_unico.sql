/* =====================================================================
   03_indice_administrador_unico.sql  -  La base de datos impide un SEGUNDO
   Administrador (la aplicación ya lo valida; este índice es la segunda barrera).

   Crea un índice único FILTRADO sobre usuario(id_rol) que solo vale para las
   filas con el rol Administrador: puede haber muchos usuarios Tradicionales, pero
   un solo Administrador.

   Requisitos:
     * Ejecutar después de 01 y 02 (necesita que exista el rol 'Administrador').
     * Si la base ya tiene más de un Administrador, el script avisa y no crea el índice.
     * Un índice filtrado exige QUOTED_IDENTIFIER ON (la línea siguiente); pyodbc ya
       lo usa por defecto, así que la aplicación no necesita cambios.

   Uso:
     sqlcmd -S 127.0.0.1,1433 -U sa -C -d proveedores_db -b -i sql/03_indice_administrador_unico.sql
   ===================================================================== */
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET NOCOUNT ON;
GO

IF EXISTS (SELECT 1 FROM sys.indexes
           WHERE name = N'UX_usuario_un_administrador'
             AND object_id = OBJECT_ID(N'dbo.usuario'))
BEGIN
    PRINT N'El índice UX_usuario_un_administrador ya existe.';
END
ELSE
BEGIN
    DECLARE @id_rol INT = (SELECT id_rol FROM dbo.rol WHERE nombre = N'Administrador');

    IF @id_rol IS NULL
        THROW 50001, N'No existe el rol Administrador. Ejecuta antes 02_datos_iniciales.sql.', 1;

    IF (SELECT COUNT(*) FROM dbo.usuario WHERE id_rol = @id_rol) > 1
        THROW 50002, N'Hay más de un Administrador. Deja solo uno antes de crear el índice.', 1;

    -- El filtro de un índice no admite variables, por eso se arma la sentencia con el id real.
    DECLARE @sql NVARCHAR(400) =
        N'CREATE UNIQUE INDEX UX_usuario_un_administrador ON dbo.usuario (id_rol) '
        + N'WHERE id_rol = ' + CAST(@id_rol AS NVARCHAR(10)) + N';';
    EXEC (@sql);
    PRINT N'Índice UX_usuario_un_administrador creado.';
END
GO
