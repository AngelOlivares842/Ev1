# ControlVentas (Aplicación de Control de Ventas)

Proyecto Django simple para gestionar productos, clientes y ventas (cabecera + detalle).

Contiene:
- Modelos: `Producto`, `Cliente`, `Venta` (cabecera) y `VentaDetalle` (líneas).
- Panel de admin con inlines para detalles de venta y acciones administrativas.
- Lógica de stock transaccional al registrar ventas.
- Eliminación lógica (soft-delete) de productos por defecto.

---

## Requisitos

- Python 3.11+ (el proyecto se probó con 3.11/3.13 en distintos entornos)
- Dependencias listadas en `requirements.txt`

---

## Configuración local (rápida)

1. Crear y activar un entorno virtual:

Windows (cmd.exe):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS (bash/zsh):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```cmd
pip install -r requirements.txt
```

3. Variables de entorno mínimas (ejemplo `.env` o en tu plataforma de despliegue):

- `SECRET_KEY` — clave secreta de Django.
- `DATABASE_URL` — URL de conexión a Postgres (ej.: Supabase). Asegúrate de incluir `?sslmode=require` si tu proveedor lo requiere.
- `DEBUG` — `True`/`False` (en producción debe estar en `False`).

Ejemplo `DATABASE_URL` (Supabase pooler):

postgresql://user:password@aws-1-us-east-2.pooler.supabase.com:6543/dbname?sslmode=require

4. Migraciones y superusuario:

```cmd
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Ejecutar servidor local:

```cmd
python manage.py runserver
```

Accede al admin en http://127.0.0.1:8000/admin/ con el superusuario.

---

## Notas importantes sobre Supabase / despliegue en Render

- Supabase requiere TLS/SSL. Si usas su pooler el puerto suele ser `6543`. Añade `?sslmode=require` al `DATABASE_URL` o configura `OPTIONS={'sslmode':'require'}` en `DATABASES` en `settings.py`.
- Error común en deploy: "connection to server ... port 6543 failed: Connection refused" — las causas habituales son:
	- `DATABASE_URL` incorrecta (host/puerto/usuario/clave
	- la instancia o pooler no está accesible desde el host del deploy
	- falta `sslmode=require` en la URL
	- límite de conexiones alcanzado

- En Render / otros PaaS, configura `DATABASE_URL` exactamente como Supabase lo provee. Si tienes problemas, abre una shell en la instancia (one-off) y prueba una conexión con `psql` o un pequeño script Python para reproducir el fallo.

---

## Comportamiento de borrado (soft-delete)

- Los `Producto` se marcan por defecto con `activo=False` en lugar de borrarse físicamente. Esto preserva historial y evita pérdida accidental de datos.
- En el admin los `Producto` inactivos están ocultos por defecto, pero puedes verlos usando el filtro `Activo` o añadiendo `?show_inactive=1` en la URL del changelist.
- Si necesitas borrado físico (hard delete) puedo añadir una acción del admin que haga `queryset.delete()` (advertencia: `VentaDetalle` y `Venta` pueden verse afectadas por cascada).

---

## Administración y características añadidas

- `ProductoAdmin` tiene filtros, acciones (marcar activo/inactivo) y eliminación lógica desde el admin.
- `VentaAdmin` incluye un inline (`VentaDetalleInline`) para manejar líneas de venta.
- Al crear una `Venta` desde el admin se decrementa el stock automáticamente (sólo en creación nueva). La edición de ventas que cambien cantidades requiere lógica adicional para ajustar el stock correctamente (puedo implementarla si la necesitas).
- `VentaDetalle` valida que no se venda más unidades de las que hay en stock.
- Existe un endpoint admin para exportar ventas por rango de fechas (CSV):

```
/admin/inventario/venta/reporte-por-fechas/?start=YYYY-MM-DD&end=YYYY-MM-DD
```

---

## Tests y calidad

- No incluí tests automáticos en esta etapa. Recomendado añadir al menos:
	- Test para creación de venta que verifique decremento de stock.
	- Test para validación de cantidad mayor al stock.

---

## Deploy (Render / Heroku / Supabase)

- Añade las variables de entorno en el dashboard del proveedor (`SECRET_KEY`, `DATABASE_URL`, `DEBUG=False`).
- Asegúrate de que `DATABASE_URL` incluya `sslmode=require` si es necesario.
- Comprueba logs de la plataforma si hay errores de conexión a la DB.

---

Si quieres, puedo:

- Añadir una acción del admin para borrado físico (hard delete) con confirmación.
- Implementar soporte para editar ventas (ajustar stock por diferencias).
- Añadir tests unitarios y CI básico.

Indícame cuál de esas tareas quieres que haga a continuación.