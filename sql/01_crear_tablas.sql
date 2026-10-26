/* =====================================================================
   01_crear_tablas.sql  -  Crea las 9 tablas del sistema (SQL Server).
   Se generó a partir de diccionario-de-datos.md.

   Uso (sobre una base de datos vacía; el script NO crea la base):
     CREATE DATABASE proveedores_db;
     sqlcmd -S 127.0.0.1,1433 -U sa -C -d proveedores_db -b -i sql/01_crear_tablas.sql

   Se puede ejecutar varias veces: cada tabla se crea solo si no existe.
   Orden de ejecución: 01_crear_tablas, 02_datos_iniciales, 03_indice_administrador_unico
   y, por último, python src/crear_admin.py.
   ===================================================================== */
SET NOCOUNT ON;
GO

/* 1. ciudad ---------------------------------------------------------- */
IF OBJECT_ID(N'dbo.ciudad', N'U') IS NULL
CREATE TABLE dbo.ciudad (
    id_ciudad    INT IDENTITY(1,1) NOT NULL,
    nombre       NVARCHAR(50)      NOT NULL,
    departamento NVARCHAR(50)      NOT NULL,
    CONSTRAINT PK_ciudad PRIMARY KEY (id_ciudad)
);
GO

/* 2. categoria ------------------------------------------------------- */
IF OBJECT_ID(N'dbo.categoria', N'U') IS NULL
CREATE TABLE dbo.categoria (
    id_categoria INT IDENTITY(1,1) NOT NULL,
    nombre       NVARCHAR(50)      NOT NULL,
    descripcion  NVARCHAR(200)     NULL,
    estado       BIT               NOT NULL CONSTRAINT DF_categoria_estado DEFAULT 1,
    CONSTRAINT PK_categoria PRIMARY KEY (id_categoria),
    CONSTRAINT UQ_categoria_nombre UNIQUE (nombre)
);
GO

/* 3. tipo_documento -------------------------------------------------- */
IF OBJECT_ID(N'dbo.tipo_documento', N'U') IS NULL
CREATE TABLE dbo.tipo_documento (
    id_tipo_documento INT IDENTITY(1,1) NOT NULL,
    nombre            VARCHAR(50)       NOT NULL,
    descripcion       NVARCHAR(200)     NULL,
    CONSTRAINT PK_tipo_documento PRIMARY KEY (id_tipo_documento),
    CONSTRAINT UQ_tipo_documento_nombre UNIQUE (nombre)
);
GO

/* 4. rol ------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.rol', N'U') IS NULL
CREATE TABLE dbo.rol (
    id_rol      INT IDENTITY(1,1) NOT NULL,
    nombre      VARCHAR(50)       NOT NULL,
    descripcion NVARCHAR(200)     NULL,
    CONSTRAINT PK_rol PRIMARY KEY (id_rol),
    CONSTRAINT UQ_rol_nombre UNIQUE (nombre)
);
GO

/* 5. proveedor ------------------------------------------------------- */
IF OBJECT_ID(N'dbo.proveedor', N'U') IS NULL
CREATE TABLE dbo.proveedor (
    id_proveedor INT IDENTITY(1,1) NOT NULL,
    nit          VARCHAR(20)       NOT NULL,
    nombre       NVARCHAR(200)     NOT NULL,
    direccion    NVARCHAR(200)     NULL,
    estado       BIT               NOT NULL CONSTRAINT DF_proveedor_estado DEFAULT 1,
    telefono     VARCHAR(20)       NULL,
    correo       VARCHAR(100)      NULL,
    id_ciudad    INT               NOT NULL,
    CONSTRAINT PK_proveedor PRIMARY KEY (id_proveedor),
    CONSTRAINT UQ_proveedor_nit UNIQUE (nit),
    CONSTRAINT FK_proveedor_ciudad FOREIGN KEY (id_ciudad) REFERENCES dbo.ciudad (id_ciudad)
);
GO

/* 6. producto -------------------------------------------------------- */
IF OBJECT_ID(N'dbo.producto', N'U') IS NULL
CREATE TABLE dbo.producto (
    id_producto   INT IDENTITY(1,1) NOT NULL,
    codigo        VARCHAR(30)       NOT NULL,
    nombre        NVARCHAR(200)     NOT NULL,
    descripcion   NVARCHAR(250)     NULL,
    unidad_medida VARCHAR(20)       NULL,
    estado        BIT               NOT NULL CONSTRAINT DF_producto_estado DEFAULT 1,
    id_categoria  INT               NOT NULL,
    CONSTRAINT PK_producto PRIMARY KEY (id_producto),
    CONSTRAINT UQ_producto_codigo UNIQUE (codigo),
    CONSTRAINT FK_producto_categoria FOREIGN KEY (id_categoria)
        REFERENCES dbo.categoria (id_categoria)
);
GO

/* 7. proveedor_producto (llave primaria compuesta) -------------------- */
IF OBJECT_ID(N'dbo.proveedor_producto', N'U') IS NULL
CREATE TABLE dbo.proveedor_producto (
    id_proveedor    INT           NOT NULL,
    id_producto     INT           NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    dias_entrega    SMALLINT      NOT NULL CONSTRAINT DF_proveedor_producto_dias DEFAULT 0,
    estado          BIT           NOT NULL CONSTRAINT DF_proveedor_producto_estado DEFAULT 1,
    CONSTRAINT PK_proveedor_producto PRIMARY KEY (id_proveedor, id_producto),
    CONSTRAINT FK_pp_proveedor FOREIGN KEY (id_proveedor) REFERENCES dbo.proveedor (id_proveedor),
    CONSTRAINT FK_pp_producto  FOREIGN KEY (id_producto)  REFERENCES dbo.producto (id_producto)
);
GO

/* 8. usuario --------------------------------------------------------- */
IF OBJECT_ID(N'dbo.usuario', N'U') IS NULL
CREATE TABLE dbo.usuario (
    id_usuario        INT IDENTITY(1,1) NOT NULL,
    nombre_usuario    VARCHAR(50)       NOT NULL,
    nombre            NVARCHAR(50)      NOT NULL,
    apellido          NVARCHAR(50)      NOT NULL,
    contrasena_hash   VARCHAR(255)      NOT NULL,
    estado            BIT               NOT NULL CONSTRAINT DF_usuario_estado DEFAULT 1,
    correo            VARCHAR(100)      NULL,
    telefono          VARCHAR(20)       NULL,
    numero_documento  VARCHAR(20)       NOT NULL,
    id_rol            INT               NOT NULL,
    id_tipo_documento INT               NOT NULL,
    creado_por        INT               NULL,
    CONSTRAINT PK_usuario PRIMARY KEY (id_usuario),
    CONSTRAINT UQ_usuario_nombre_usuario UNIQUE (nombre_usuario),
    CONSTRAINT FK_usuario_rol FOREIGN KEY (id_rol) REFERENCES dbo.rol (id_rol),
    CONSTRAINT FK_usuario_tipo_documento FOREIGN KEY (id_tipo_documento)
        REFERENCES dbo.tipo_documento (id_tipo_documento),
    CONSTRAINT FK_usuario_creado_por FOREIGN KEY (creado_por) REFERENCES dbo.usuario (id_usuario)
);
GO

/* 9. bitacora -------------------------------------------------------- */
IF OBJECT_ID(N'dbo.bitacora', N'U') IS NULL
CREATE TABLE dbo.bitacora (
    id_bitacora        INT IDENTITY(1,1) NOT NULL,
    id_usuario         INT               NOT NULL,
    fecha_hora_entrada DATETIME2(0)      NOT NULL,
    fecha_hora_salida  DATETIME2(0)      NULL,
    CONSTRAINT PK_bitacora PRIMARY KEY (id_bitacora),
    CONSTRAINT FK_bitacora_usuario FOREIGN KEY (id_usuario) REFERENCES dbo.usuario (id_usuario)
);
GO
