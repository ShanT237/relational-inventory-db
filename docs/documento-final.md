---
title: "Sistema de Gestión de Proveedores y Productos"
subtitle: "Proyecto final de Bases de Datos I — Programa de Ingeniería de Sistemas y Computación, Universidad del Quindío (2026-II)"
author: "Nombre Apellido, Nombre Apellido, Nombre Apellido"
---

# 1. Explicación general de la aplicación

## 1.1 Problema que resuelve

Las empresas comerciales necesitan saber a qué proveedores pueden hacerles pedidos de sus productos. El sistema guarda esa información y permite consultarla. Registra:

- **Proveedores**, ubicados en cualquier ciudad de Colombia.
- **Productos**, con sus datos y la categoría a la que pertenecen.
- **Qué productos puede enviar cada proveedor**, con el precio unitario y los días de entrega. Un proveedor puede suministrar varios productos y un producto puede conseguirse con varios proveedores.
- **Usuarios**, con inicio de sesión y permisos según su tipo.
- **Bitácora**, con la fecha y la hora de entrada y de salida de cada usuario.

## 1.2 Alcance y tecnologías

Es una aplicación de escritorio. El enunciado prohíbe usar frameworks, así que solo se usa la biblioteca estándar de Python y librerías puntuales.

| Componente | Tecnología | Uso |
|------------|------------|-----|
| Lenguaje | Python 3 | Lógica de la aplicación |
| Interfaz gráfica | Tkinter | Ventanas y formularios |
| Base de datos | Microsoft SQL Server (en Docker) | Almacenamiento de los datos |
| Conexión | `pyodbc` y ODBC Driver 18 for SQL Server | Ejecutar consultas desde Python |
| Reportes | `reportlab` | Reportes en PDF |
| Seguridad | `hashlib` (PBKDF2-SHA256, 200 000 iteraciones) | Cifrado de contraseñas |

## 1.3 Usuarios y permisos

| Tipo de usuario | Cantidad | Qué puede hacer |
|-----------------|----------|-----------------|
| Administrador | Solo 1 | Todo lo del Tradicional, más crear y modificar usuarios y ver la bitácora |
| Tradicional | Varios | Crear, consultar, modificar y eliminar datos (entidades y transacciones), consultas y reportes |
| Esporádico | Varios | Solo consultas |

Las contraseñas se guardan cifradas con una sal aleatoria por usuario. Solo el Administrador crea usuarios, y el sistema impide tener un segundo Administrador tanto en la lógica de la aplicación como con un índice único en la base de datos (`sql/03_indice_administrador_unico.sql`).

## 1.4 Módulos

| Módulo | Función | Acceso |
|--------|---------|--------|
| Ingreso | Valida usuario y contraseña y abre el registro en la bitácora | Todos |
| Entidades | CRUD de ciudades, categorías, proveedores y productos | Administrador, Tradicional |
| Transacciones | Asigna a cada proveedor los productos que suministra, con precio y días de entrega | Administrador, Tradicional |
| Consultas | Las cinco consultas mínimas del enunciado | Todos |
| Reportes | Cinco reportes en PDF con filtros | Administrador, Tradicional |
| Auditoría | Gestión de usuarios y bitácora de entrada y salida | Solo Administrador |

Al iniciar sesión se crea un registro en `bitacora` con la hora de entrada; al cerrar sesión se completa la hora de salida.

## 1.5 Consultas

1. Proveedores con su ciudad y los productos que suministran (JOIN de 4 tablas).
2. Productos con su categoría y los proveedores que los ofrecen, con precio y días de entrega (JOIN de 4 tablas).
3. Bitácora de ingresos con el usuario y su rol (JOIN de 3 tablas).
4. Proveedores que ofrecen productos con precio mayor al promedio (subconsulta).
5. Productos que no tienen ningún proveedor asignado (subconsulta con `NOT EXISTS`).

## 1.6 Reportes en PDF

Cada reporte se genera desde el menú **Reportes**: el usuario elige el filtro en una lista desplegable, el PDF se guarda en la carpeta `reportes/` y se abre automáticamente. Todos llevan encabezado, título, filtros aplicados, tabla, fecha, hora, usuario y número de página.

| Reporte | Filtro |
|---------|--------|
| Productos que suministra un proveedor | Proveedor |
| Proveedores por ciudad con sus productos | Ciudad o departamento |
| Proveedores de un producto con precios | Producto |
| Productos de una categoría | Categoría |
| Cantidad de productos por categoría | Estado (todos, activos o inactivos) |

## 1.7 Arquitectura

El código se organiza en capas y las vistas no contienen SQL:

- **Presentación:** `vistas/` (ventanas de Tkinter) y `controladores/` (reciben la acción de la vista y llaman al servicio).
- **Lógica:** `servicios/` (reglas del negocio, validaciones, permisos por rol y generación de PDF).
- **Datos:** `repositorios/` (acceso a SQL Server con `pyodbc`; todas las consultas usan parámetros para evitar inyección SQL).
- **Dominio:** `dominio/` (entidades y el error de reglas del negocio).

# 2. Diagrama entidad-relación

![Diagrama entidad-relación del sistema](img/diagrama-er.png)

El diagrama se edita en `docs/diagrama-er.drawio` (draw.io). Las relaciones son:

| Entidad 1 | Relación | Entidad 2 | Cardinalidad |
|-----------|----------|-----------|--------------|
| Ciudad | ubica | Proveedor | 1 : N |
| Categoría | clasifica | Producto | 1 : N |
| Proveedor | suministra | Producto | N : M (resuelta con `proveedor_producto`) |
| Rol | tiene | Usuario | 1 : N |
| Tipo de documento | identifica | Usuario | 1 : N |
| Usuario | genera | Bitácora | 1 : N |
| Usuario | crea | Usuario | 1 : N (recursiva, `creado_por`) |

# 3. Diagrama relacional normalizado

Notación: **PK** llave primaria, **FK** llave foránea (→ tabla referenciada), **UQ** valor único.

```text
ciudad(PK id_ciudad, nombre, departamento)

categoria(PK id_categoria, nombre UQ, descripcion, estado)

tipo_documento(PK id_tipo_documento, nombre UQ, descripcion)

rol(PK id_rol, nombre UQ, descripcion)

proveedor(PK id_proveedor, nit UQ, nombre, direccion, estado, telefono, correo,
          FK id_ciudad → ciudad)

producto(PK id_producto, codigo UQ, nombre, descripcion, unidad_medida, estado,
         FK id_categoria → categoria)

proveedor_producto(PK,FK id_proveedor → proveedor, PK,FK id_producto → producto,
                   precio_unitario, dias_entrega, estado)

usuario(PK id_usuario, nombre_usuario UQ, nombre, apellido, contrasena_hash, estado,
        correo, telefono, numero_documento,
        FK id_rol → rol, FK id_tipo_documento → tipo_documento,
        FK creado_por → usuario)

bitacora(PK id_bitacora, FK id_usuario → usuario, fecha_hora_entrada, fecha_hora_salida)
```

## 3.1 Justificación de la normalización

- **Primera forma normal:** todas las columnas guardan un solo valor (un teléfono, un correo, una fecha); no hay grupos repetidos. La lista de productos de un proveedor no se guarda en una columna, sino en filas de `proveedor_producto`.
- **Segunda forma normal:** `precio_unitario`, `dias_entrega` y `estado` de `proveedor_producto` dependen de la llave completa (`id_proveedor`, `id_producto`): el precio es de *ese* producto con *ese* proveedor. Las demás tablas tienen llave simple, así que no pueden tener dependencias parciales.
- **Tercera forma normal:** los datos que se repetirían se separaron en tablas propias para que no dependan de atributos que no son llave: el nombre de la categoría, de la ciudad, del rol y del tipo de documento se guardan una sola vez y se referencian con una llave foránea. El departamento se mantiene como atributo de `ciudad` porque la aplicación solo lo usa para ubicar a los proveedores y filtrar reportes; no se necesita como entidad aparte.
- **Reglas que el esquema no controla** y se validan en la aplicación: un solo Administrador (además protegido con un índice único), permisos por rol, y que una oferta solo pueda estar activa si su proveedor y su producto lo están.
