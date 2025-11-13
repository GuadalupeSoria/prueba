# Coliving Match Demo

Este repositorio contiene un backend de ejemplo construido con **FastAPI** que combina funcionalidades tipo Tinder y Airbnb para facilitar la búsqueda de compañeros de piso compatibles. Se incluyen componentes clave inspirados en aplicaciones como Badi:

- Algoritmo de *matching* basado en gustos, estilo de vida y presupuesto.
- Integración con un fichero de morosos simulado para filtrar perfiles con deudas.
- Verificación biométrica facial para validar la existencia del usuario.
- Verificación de propiedades mediante contratos digitalizados.

## Requisitos

- Python 3.10 o superior
- `pip` o `uv` para instalar dependencias

Instala las dependencias de ejecución y desarrollo con:

```bash
pip install -e .[dev]
```

## Ejecución del servidor

Lanza el servidor local usando `uvicorn`:

```bash
uvicorn app.main:app --reload
```

El endpoint de salud estará disponible en `http://127.0.0.1:8000/health`.

## Uso de la API

1. **Crear usuario** – Envía un `POST /users` con preferencias y se comprobará automáticamente si figura en el fichero de morosos.
2. **Verificar identidad** – Usa `POST /users/{id}/verify` enviando `{ "selfie_reference": "ref" }` en el cuerpo para marcar al usuario como verificado facialmente.
3. **Publicar propiedad** – Envía `POST /properties` con los datos y amenities de la vivienda.
4. **Verificar contrato** – Con `POST /properties/{id}/verify` y el cuerpo `{ "contract_reference": "ref" }` se marca la propiedad como validada documentalmente.
5. **Obtener matches** – Recupera las coincidencias mediante `GET /users/{id}/matches`.

La carpeta `app/services` contiene implementaciones stub que deberían conectarse a proveedores reales en un entorno de producción.

## Pruebas

Ejecuta los tests de Pytest con:

```bash
pytest
```

## Próximos pasos sugeridos

- Persistencia real (PostgreSQL + SQLModel) para usuarios y propiedades.
- Integración real con servicios de verificación biométrica y registros de morosos.
- Motor de recomendaciones basado en ML y *feedback* explícito de los usuarios.
- Aplicación móvil o web que consuma la API para ofrecer experiencias tipo swipe/match.
