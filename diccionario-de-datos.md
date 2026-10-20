# Diccionario de datos

**Proyecto:** Sistema de Gestión de Proveedores y Productos
**Asignatura:** Bases de Datos I — Programa de Ingeniería de Sistemas y Computación, Universidad del Quindío
**Motor de base de datos:** Microsoft SQL Server

## Convenciones

- **PK**: llave primaria. **FK**: llave foránea. **UQ**: valor único.
- `estado` es de tipo `BIT`: `1` = activo, `0` = inactivo. Se usa para el borrado lógico.
- `NVARCHAR` guarda texto con tildes y caracteres especiales (Unicode). `VARCHAR` se usa para códigos y datos sin acentos.
- Las llaves primarias numéricas son autoincrementales con `IDENTITY(1,1)`.

## Resumen de tablas

| # | Tabla | Descripción |
|---|-------|-------------|
| 1 | `ciudad` | Ciudades de Colombia donde se ubican los proveedores |
| 2 | `categoria` | Familias en las que se clasifican los productos |
| 3 | `tipo_documento` | Tipos de documento de identidad de los usuarios |
| 4 | `rol` | Tipos de usuario del sistema |
| 5 | `proveedor` | Proveedores a quienes se pueden hacer pedidos |
| 6 | `producto` | Productos que se pueden adquirir |
| 7 | `proveedor_producto` | Productos que suministra cada proveedor, con precio y tiempo de entrega |
| 8 | `usuario` | Usuarios que ingresan a la aplicación |
| 9 | `bitacora` | Registro de entrada y salida de los usuarios |

---

## 1. `ciudad`

Almacena las ciudades donde pueden estar los proveedores.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_ciudad` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador de la ciudad |
| `nombre` | `NVARCHAR(50)` | No | | | Nombre de la ciudad |
| `departamento` | `NVARCHAR(50)` | No | | | Departamento al que pertenece la ciudad |

## 2. `categoria`

Almacena las categorías que agrupan los productos en familias.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_categoria` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador de la categoría |
| `nombre` | `NVARCHAR(50)` | No | UQ | | Nombre de la categoría. No se repite |
| `descripcion` | `NVARCHAR(200)` | Sí | | | Descripción de la categoría |
| `estado` | `BIT` | No | | `1` | Indica si la categoría está activa |

## 3. `tipo_documento`

Almacena los tipos de documento de identidad (por ejemplo, cédula de ciudadanía).

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_tipo_documento` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador del tipo de documento |
| `nombre` | `VARCHAR(50)` | No | UQ | | Nombre del tipo de documento. No se repite |
| `descripcion` | `NVARCHAR(200)` | Sí | | | Descripción del tipo de documento |

## 4. `rol`

Almacena los tipos de usuario del sistema: Administrador, Tradicional y Esporádico.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_rol` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador del rol |
| `nombre` | `VARCHAR(50)` | No | UQ | | Nombre del rol. No se repite |
| `descripcion` | `NVARCHAR(200)` | Sí | | | Descripción de los permisos del rol |

## 5. `proveedor`

Almacena los datos de los proveedores.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_proveedor` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador del proveedor |
| `nit` | `VARCHAR(20)` | No | UQ | | NIT del proveedor. No se repite |
| `nombre` | `NVARCHAR(200)` | No | | | Nombre o razón social |
| `direccion` | `NVARCHAR(200)` | Sí | | | Dirección del proveedor |
| `estado` | `BIT` | No | | `1` | Indica si el proveedor está activo |
| `telefono` | `VARCHAR(20)` | Sí | | | Teléfono de contacto |
| `correo` | `VARCHAR(100)` | Sí | | | Correo electrónico de contacto |
| `id_ciudad` | `INT` | No | FK → `ciudad.id_ciudad` | | Ciudad donde se ubica el proveedor |

## 6. `producto`

Almacena los datos de los productos.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_producto` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador del producto |
| `codigo` | `VARCHAR(30)` | No | UQ | | Código del producto. No se repite |
| `nombre` | `NVARCHAR(200)` | No | | | Nombre del producto |
| `descripcion` | `NVARCHAR(250)` | Sí | | | Descripción del producto |
| `unidad_medida` | `VARCHAR(20)` | Sí | | | Unidad en que se mide el producto (kg, litro, unidad) |
| `estado` | `BIT` | No | | `1` | Indica si el producto está activo |
| `id_categoria` | `INT` | No | FK → `categoria.id_categoria` | | Categoría a la que pertenece el producto |

## 7. `proveedor_producto`

Tabla intermedia de la relación muchos a muchos entre proveedor y producto. Un proveedor puede suministrar varios productos y un producto puede conseguirse con varios proveedores.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_proveedor` | `INT` | No | PK, FK → `proveedor.id_proveedor` | | Proveedor que suministra el producto |
| `id_producto` | `INT` | No | PK, FK → `producto.id_producto` | | Producto que suministra el proveedor |
| `precio_unitario` | `DECIMAL(12,2)` | No | | | Precio por unidad que ofrece el proveedor |
| `dias_entrega` | `SMALLINT` | No | | `0` | Días que tarda el proveedor en entregar |
| `estado` | `BIT` | No | | `1` | Indica si el proveedor sigue ofreciendo el producto |

La llave primaria es compuesta: (`id_proveedor`, `id_producto`). Así un proveedor no puede repetir el mismo producto.

## 8. `usuario`

Almacena los usuarios que ingresan a la aplicación.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_usuario` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador del usuario |
| `nombre_usuario` | `VARCHAR(50)` | No | UQ | | Nombre con el que inicia sesión. No se repite |
| `nombre` | `NVARCHAR(50)` | No | | | Nombres de la persona |
| `apellido` | `NVARCHAR(50)` | No | | | Apellidos de la persona |
| `contrasena_hash` | `VARCHAR(255)` | No | | | Contraseña cifrada. Nunca se guarda en texto plano |
| `estado` | `BIT` | No | | `1` | Indica si el usuario puede ingresar |
| `correo` | `VARCHAR(100)` | Sí | | | Correo electrónico |
| `telefono` | `VARCHAR(20)` | Sí | | | Teléfono |
| `numero_documento` | `VARCHAR(20)` | No | | | Número del documento de identidad |
| `id_rol` | `INT` | No | FK → `rol.id_rol` | | Rol del usuario |
| `id_tipo_documento` | `INT` | No | FK → `tipo_documento.id_tipo_documento` | | Tipo de documento del usuario |
| `creado_por` | `INT` | Sí | FK → `usuario.id_usuario` | | Administrador que creó al usuario. Es `NULL` para el primer Administrador |

## 9. `bitacora`

Almacena la entrada y la salida de los usuarios del sistema.

| Columna | Tipo de dato | Nulo | Clave | Valor por defecto | Descripción |
|---------|--------------|------|-------|-------------------|-------------|
| `id_bitacora` | `INT IDENTITY(1,1)` | No | PK | Autoincremental | Identificador del registro |
| `id_usuario` | `INT` | No | FK → `usuario.id_usuario` | | Usuario que ingresó al sistema |
| `fecha_hora_entrada` | `DATETIME2(0)` | No | | | Fecha y hora del ingreso |
| `fecha_hora_salida` | `DATETIME2(0)` | Sí | | | Fecha y hora de la salida. Es `NULL` mientras la sesión sigue abierta |

---

## Relaciones entre tablas

| Tabla padre (lado 1) | Tabla hija (lado N) | Llave foránea | Significado |
|----------------------|---------------------|---------------|-------------|
| `ciudad` | `proveedor` | `proveedor.id_ciudad` | Una ciudad ubica a muchos proveedores |
| `categoria` | `producto` | `producto.id_categoria` | Una categoría clasifica muchos productos |
| `proveedor` | `proveedor_producto` | `proveedor_producto.id_proveedor` | Un proveedor suministra muchos productos |
| `producto` | `proveedor_producto` | `proveedor_producto.id_producto` | Un producto es suministrado por muchos proveedores |
| `rol` | `usuario` | `usuario.id_rol` | Un rol lo tienen muchos usuarios |
| `tipo_documento` | `usuario` | `usuario.id_tipo_documento` | Un tipo de documento identifica a muchos usuarios |
| `usuario` | `bitacora` | `bitacora.id_usuario` | Un usuario genera muchos registros de bitácora |
| `usuario` | `usuario` | `usuario.creado_por` | Un Administrador crea muchos usuarios (relación recursiva) |

## Reglas que el esquema no controla

Estas reglas del enunciado se validan en la lógica de la aplicación:

- **Un solo Administrador.** El sistema no permite crear un segundo usuario con ese rol.
- **Solo el Administrador crea usuarios.** Los demás roles no ven ese módulo.
- **Datos iniciales de `rol`:** `Administrador`, `Tradicional` y `Esporádico`.
- **Permisos por rol:** el Tradicional ejecuta los CRUD y el Esporádico solo hace consultas.
