# Sistema de Gestión de Proveedores y Productos

Proyecto final de **Bases de Datos I** — Programa de Ingeniería de Sistemas y Computación, Universidad del Quindío (2026-II).

**Integrantes:** Nombre Apellido, Nombre Apellido, Nombre Apellido

## 1. Descripción

Las empresas comerciales necesitan saber a qué proveedores pueden hacer pedidos de sus productos. Este sistema guarda esa información y permite consultarla.

La aplicación registra:

- **Proveedores**, que pueden estar en cualquier ciudad de Colombia.
- **Productos**, con sus datos y la categoría a la que pertenecen.
- **Qué productos puede enviar cada proveedor**, con el precio y los días de entrega. Un proveedor puede proveer varios productos y un producto puede adquirirse con varios proveedores.
- **Usuarios**, con inicio de sesión y permisos según su tipo.
- **Bitácora**, con la fecha y hora de entrada y salida de cada usuario.

## 2. Alcance

Es una **aplicación de escritorio**. El enunciado prohíbe usar frameworks, así que solo se usan la biblioteca estándar de Python y librerías puntuales para conectarse a la base de datos y generar PDF.

## 3. Tecnologías

| Componente | Tecnología | Uso |
|------------|------------|-----|
| Lenguaje | Python 3 | Lógica de la aplicación |
| Interfaz gráfica | Tkinter (incluido en Python) | Ventanas y formularios |
| Base de datos | Microsoft SQL Server | Almacenamiento de datos (designado por el profesor) |
| Conexión | `pyodbc` + ODBC Driver for SQL Server | Ejecutar consultas desde Python |
| Reportes | `reportlab` | Generar los reportes en PDF |
| Seguridad | `hashlib` (PBKDF2) | Cifrar las contraseñas |

Tkinter, `pyodbc` y `reportlab` son librerías, no frameworks.

## 4. Usuarios y permisos

| Tipo de usuario | Cantidad | Qué puede hacer |
|-----------------|----------|-----------------|
| **Administrador** | Solo 1 | Todo lo del Tradicional, más crear y modificar usuarios y ver la bitácora |
| **Tradicional** | Varios | CRUD de los datos (crear, consultar, modificar, eliminar), consultas y reportes |
| **Esporádico** | Varios | Solo consultas |

Solo el Administrador puede crear usuarios nuevos. Las contraseñas se guardan cifradas.

> **Decisión sobre los reportes:** por ahora el Esporádico **no** genera reportes (el enunciado le deja solo consultas). Si el equipo decide permitírselo, hay que cambiar `requiere_modificar` por `requiere_sesion` en `ReporteServicio.construir` y mostrar la sección Reportes a ese rol en `menu_principal_vista.py`.

## 5. Módulos

| Módulo | Función | Acceso |
|--------|---------|--------|
| **Ingreso** | Inicio de sesión. Valida usuario y contraseña, y abre el registro en la bitácora | Todos |
| **Entidades** | CRUD de ciudades, categorías, proveedores y productos | Administrador, Tradicional |
| **Transacciones** | Asignar a cada proveedor los productos que suministra, con precio y días de entrega | Administrador, Tradicional |
| **Consultas** | Las cinco consultas mínimas del enunciado | Todos |
| **Reportes** | Los cinco reportes en PDF con filtros | Administrador, Tradicional |
| **Auditoría** | Gestión de usuarios y bitácora de entrada y salida | Solo Administrador |

Al iniciar sesión se crea un registro en `bitacora` con la fecha y hora de entrada. Al cerrar sesión se completa la fecha y hora de salida.

## 6. Modelo de datos

La base de datos tiene 9 tablas: `ciudad`, `categoria`, `tipo_documento`, `rol`, `proveedor`, `producto`, `proveedor_producto`, `usuario` y `bitacora`.

- Diagrama entidad-relación: `docs/diagrama-er.drawio`
- Diccionario de datos: [`diccionario-de-datos.md`](diccionario-de-datos.md)
- Scripts SQL: [`sql/`](sql/) (`01_crear_tablas.sql`, `02_datos_iniciales.sql` y `03_indice_administrador_unico.sql`)
- Documento final (explicación, diagramas y diccionario): [`docs/documento-final.md`](docs/documento-final.md)

La relación muchos a muchos entre proveedor y producto se resuelve con la tabla `proveedor_producto`.

## 7. Consultas mínimas

### Consultas con JOIN (3 tablas o más)

1. **Proveedores con su ciudad y los productos que suministran** (`proveedor`, `ciudad`, `proveedor_producto`, `producto`).
2. **Productos con su categoría y los proveedores que los ofrecen, con precio y días de entrega** (`producto`, `categoria`, `proveedor_producto`, `proveedor`).
3. **Bitácora de ingresos con el usuario y su rol** (`bitacora`, `usuario`, `rol`).

```sql
-- Consulta 1
SELECT p.nombre AS proveedor, c.nombre AS ciudad, c.departamento,
       pr.nombre AS producto, pp.precio_unitario
FROM proveedor p
JOIN ciudad c ON c.id_ciudad = p.id_ciudad
JOIN proveedor_producto pp ON pp.id_proveedor = p.id_proveedor
JOIN producto pr ON pr.id_producto = pp.id_producto;
```

### Consultas con subconsultas (2 tablas)

4. **Proveedores que ofrecen productos con precio mayor al promedio** (`proveedor`, `proveedor_producto`).
5. **Productos que no tienen ningún proveedor asignado** (`producto`, `proveedor_producto`).

```sql
-- Consulta 4
SELECT p.nit, p.nombre
FROM proveedor p
WHERE p.id_proveedor IN (
    SELECT pp.id_proveedor
    FROM proveedor_producto pp
    WHERE pp.precio_unitario > (SELECT AVG(precio_unitario) FROM proveedor_producto)
);

-- Consulta 5
SELECT pr.codigo, pr.nombre
FROM producto pr
WHERE NOT EXISTS (
    SELECT 1 FROM proveedor_producto pp WHERE pp.id_producto = pr.id_producto
);
```

## 8. Reportes

Todos se generan en PDF y el usuario elige los filtros en listas desplegables antes de generarlos. El PDF se guarda en la carpeta `reportes/` y se abre automáticamente. Lleva encabezado, título, filtros aplicados, tabla, fecha, hora, usuario y número de página.

**Productos y proveedores (3 reportes)**

| Reporte | Filtro del usuario |
|---------|--------------------|
| Productos que suministra un proveedor | Proveedor |
| Proveedores por ciudad con sus productos | Ciudad o departamento |
| Proveedores de un producto con precios | Producto |

**Productos y categorías (2 reportes)**

| Reporte | Filtro del usuario |
|---------|--------------------|
| Productos de una categoría | Categoría |
| Cantidad de productos por categoría | Estado (todos, activos o inactivos) |

## 9. Arquitectura

La aplicación se divide en tres capas:

- **Presentación:** ventanas de Tkinter (`vistas/`) y controladores (`controladores/`). No contiene consultas SQL.
- **Lógica:** reglas del negocio (`servicios/`), como validar permisos y el Administrador único, y la generación de PDF.
- **Datos:** acceso a SQL Server con `pyodbc` (`repositorios/`). Todas las consultas usan parámetros para evitar inyección SQL.

```text
proyecto-final-bd/
├── src/
│   ├── main.py             # arma las piezas y arranca la aplicación
│   ├── crear_admin.py      # crea el usuario Administrador (una sola vez)
│   ├── configuracion/      # datos de conexión (lee el archivo .env)
│   ├── dominio/            # entidades y errores del negocio
│   ├── repositorios/       # consultas SQL con pyodbc
│   ├── servicios/          # reglas del negocio, permisos y generador de PDF
│   ├── controladores/      # conectan las vistas con los servicios
│   └── vistas/             # ventanas de Tkinter
├── tests/                  # pruebas automáticas (unittest)
├── sql/                    # 01_crear_tablas, 02_datos_iniciales, 03_indice_administrador_unico
├── db/                     # respaldo proveedores_db.bak
├── docs/                   # diagrama-er.drawio y documento-final.md
├── reportes/               # PDF generados (no se suben a Git)
├── diccionario-de-datos.md
├── docker-compose.yml
├── restaurar-bd.ps1
├── .env.example            # plantilla de claves (cada persona crea su .env)
├── requirements.txt
└── README.md
```

## 10. Entregables

- [x] Diagrama entidad-relación
- [x] Diccionario de datos
- [x] Diagrama relacional de tablas normalizado
- [x] Explicación general de la aplicación (este documento y `docs/documento-final.md`)
- [ ] Aplicación funcionando: ingreso, entidades, transacciones, consultas, reportes y auditoría



## Cómo ejecutar el proyecto

### Primera vez (solo una vez)

1. Instalar [Docker Desktop](https://www.docker.com/products/docker-desktop/) (con WSL) y abrirlo hasta que diga "Engine running".
2. Instalar Python 3 y el "ODBC Driver 18 for SQL Server".
3. Clonar el repo y entrar a la carpeta:

```
git clone https://github.com/ShanT237/relational-inventory-db
cd relational-inventory-db
```

4. Instalar las librerías:

```
pip install -r requirements.txt
```

5. Crear tu archivo de claves: copiar `.env.example` como `.env` y escribir en `MSSQL_SA_PASSWORD` una clave que tú elijas (mínimo 8 caracteres con mayúsculas, minúsculas, números y símbolos; evita `$ " ' # \`). El archivo `.env` no se sube a Git; la clave de `sa` se pide entre los integrantes por un canal privado, nunca por el repositorio.

```
Copy-Item .env.example .env
```

6. Cargar la base de datos (tarda ~30 segundos y debe terminar con "Listo" en verde):

```
powershell -ExecutionPolicy Bypass -File restaurar-bd.ps1
```

### Cada vez que quieras usar la app

1. Abrir Docker Desktop y esperar "Engine running".
2. Prender el contenedor (botón play en Docker Desktop, o `docker compose up -d` en la carpeta del proyecto).
3. Ejecutar:

```
python src/main.py
```

4. Entrar con el usuario Administrador (usuario `jjs`). La contraseña no está en el repositorio: pídela al equipo. Si montas una base nueva desde cero, crea el Administrador con `python src/crear_admin.py`.

### Pruebas automáticas

```
python -m unittest discover -s tests -t . -v
```

### Base de datos desde cero (sin el respaldo)

Los scripts de `sql/` crean la base vacía y cargan los datos mínimos. Se ejecutan en orden sobre una base ya creada (ver el encabezado de cada script).

### Notas

- Cada persona tiene su propia copia de la BD; lo que cambie uno no lo ven los demás.
- Para volver a los datos originales, correr de nuevo `restaurar-bd.ps1`.
- Para apagar el contenedor: `docker compose stop` (no borra datos). No usar `docker compose down -v`, que sí borra todo.
- No subir `.env` ni `configuracion_local.py` a GitHub (tienen claves). Ambos están en `.gitignore`.
- La clave de `sa` solo se aplica la primera vez que se crea el contenedor. Para cambiarla en un contenedor que ya existe: `ALTER LOGIN sa WITH PASSWORD = '...'` con `sqlcmd`, y actualizar el `.env`.
