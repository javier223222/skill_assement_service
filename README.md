# Skill Assessment Service

Microservicio para evaluación de habilidades técnicas con inteligencia artificial, desarrollado con FastAPI y arquitectura hexagonal basada en Domain Driven Design (DDD).

## Tabla de Contenidos

- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Despliegue](#despliegue)
- [Estructura del Proyecto](#estructura-del-proyecto)

## Descripción

Este microservicio permite crear evaluaciones de habilidades técnicas mediante cuestionarios generados automáticamente con IA. Los usuarios pueden responder preguntas, recibir feedback personalizado y obtener reportes de sus competencias.

### Características principales:

- Generación automática de preguntas con Google Gemini AI
- Evaluación inteligente de respuestas
- Sistema de sesiones para seguimiento de progreso
- Feedback personalizado por habilidad
- Arquitectura limpia y escalable
- Integración con MongoDB y RabbitMQ
- Documentación automática con OpenAPI/Swagger

## Arquitectura

El proyecto sigue los principios de Clean Architecture y Domain Driven Design:

```
src/
├── domain/           # Entidades, repositorios abstractos y lógica de negocio
├── application/      # Casos de uso y DTOs
├── infrastructure/   # Implementaciones concretas (BD, servicios externos)
└── presentation/     # Controllers y esquemas de API
```

## Tecnologías

- **Framework**: FastAPI
- **Base de datos**: MongoDB con Beanie ODM
- **IA**: Google Gemini API
- **Mensajería**: RabbitMQ
- **Containerización**: Docker
- **Lenguaje**: Python 3.11

## Instalación

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose
- MongoDB
- RabbitMQ

### Instalación local

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd skillAssement
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno (ver sección [Configuración](#configuración))

5. Ejecutar la aplicación:
```bash
cd src
python main.py
```

### Instalación con Docker

1. Configurar variables de entorno en `.env`

2. Ejecutar con Docker Compose:
```bash
docker-compose up --build
```

## Configuración

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=skill_assessment

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Queue Names
NOTIFICATIONS_QUEUE_NAME=notifications
PROFILE_QUEUE_NAME=profile_updates
```

## Uso

Una vez iniciado el servicio, la documentación interactiva estará disponible en:

- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

### Flujo básico de uso:

1. **Crear una habilidad** - Define la habilidad a evaluar
2. **Iniciar evaluación** - Genera preguntas automáticamente
3. **Responder preguntas** - El usuario contesta el cuestionario
4. **Obtener feedback** - Recibe evaluación detallada

## API Endpoints

### Health Check

#### GET /
Verificación de estado del servicio.

**Response:**
```json
{
  "status": "ok",
  "service": "skill-assessment-service",
  "message": "Servicio funcionando correctamente"
}
```

### Skills Management

#### POST /api/v1/
Crear una nueva habilidad.

**Request Body:**
```json
{
  "name": "JavaScript",
  "description": "Conocimientos de JavaScript",
  "category": "Frontend",
  "difficulty": "intermediate"
}
```

**Response:** `201 Created`
```json
{
  "message": "Skill created successfully",
  "skill_id": "507f1f77bcf86cd799439011"
}
```

#### GET /api/v1/skills/
Obtener todas las habilidades con paginación.

**Query Parameters:**
- `skip` (int, optional): Número de elementos a omitir (default: 0)
- `limit` (int, optional): Número máximo de elementos (default: 10)

**Response:** `200 OK`
```json
{
  "skills": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "JavaScript",
      "description": "Conocimientos de JavaScript",
      "category": "Frontend",
      "difficulty": "intermediate",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### GET /api/v1/{skill_id}
Obtener una habilidad específica por ID.

**Path Parameters:**
- `skill_id` (string): ID de la habilidad

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "JavaScript",
  "description": "Conocimientos de JavaScript",
  "category": "Frontend",
  "difficulty": "intermediate",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Skill not found"
}
```

#### DELETE /api/v1/{skill_id}
Eliminar una habilidad por ID.

**Path Parameters:**
- `skill_id` (string): ID de la habilidad

**Response:** `200 OK`
```json
{
  "message": "Skill deleted successfully"
}
```

#### PATCH /api/v1/
Actualizar una habilidad existente.

**Request Body:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Advanced JavaScript",
  "description": "Conocimientos avanzados de JavaScript",
  "category": "Frontend",
  "difficulty": "advanced"
}
```

**Response:** `200 OK`
```json
{
  "message": "Skill updated successfully"
}
```

### Assessment Management

#### POST /api/v1/assement/{skill_id}
Crear una nueva evaluación para una habilidad específica.

**Path Parameters:**
- `skill_id` (string): ID de la habilidad a evaluar

**Request Body:**
```json
{
  "id_user": "user123"
}
```

**Response:** `201 Created`
```json
{
  "message": "Assessment generated successfully",
  "Assessment": {
    "session_id": "session123",
    "questions": [
      {
        "id": 1,
        "question": "¿Qué es una closure en JavaScript?",
        "options": ["A", "B", "C", "D"]
      }
    ]
  },
  "next_step": 1
}
```

#### GET /api/v1/assement/session/{session_id}
Obtener información de una sesión de evaluación.

**Path Parameters:**
- `session_id` (string): ID de la sesión

**Response:** `200 OK`
```json
{
  "id": "session123",
  "user_id": "user123",
  "skill_id": "507f1f77bcf86cd799439011",
  "status": "in_progress",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/assement/questions/{id}
Obtener una pregunta específica de la evaluación.

**Path Parameters:**
- `id` (int): ID de la pregunta

**Query Parameters:**
- `id_user` (string): ID del usuario
- `id_session` (string): ID de la sesión

**Response:** `200 OK`
```json
{
  "id": 1,
  "question": "¿Qué es una closure en JavaScript?",
  "options": ["Función anidada", "Variable global", "Método de objeto", "Bucle infinito"],
  "session_id": "session123"
}
```

#### POST /api/v1/assement/questions/{id_question}
Responder una pregunta de la evaluación.

**Path Parameters:**
- `id_question` (int): ID de la pregunta

**Request Body:**
```json
{
  "id_session": "session123",
  "id_user": "user123",
  "answer": "Función anidada"
}
```

**Response:** `201 Created`
```json
{
  "message": "Answer recorded successfully",
  "next_question": 2,
  "is_complete": false
}
```

#### PUT /api/v1/assement/questions/{id_question}
Actualizar la respuesta de una pregunta.

**Path Parameters:**
- `id_question` (int): ID de la pregunta

**Request Body:**
```json
{
  "id_session": "session123",
  "id_user": "user123",
  "answer": "Nueva respuesta"
}
```

**Response:** `200 OK`
```json
{
  "message": "Answer updated successfully"
}
```

### Feedback Management

#### GET /api/v1/assement/feedback/{session_id}
Generar y obtener feedback de una evaluación completada.

**Path Parameters:**
- `session_id` (string): ID de la sesión

**Response:** `200 OK`
```json
{
  "session_id": "session123",
  "feedback": {
    "score": 85,
    "level": "intermediate",
    "strengths": ["Conceptos básicos", "Sintaxis"],
    "areas_for_improvement": ["Async/await", "Closures"],
    "recommendations": ["Practicar promesas", "Estudiar scope"]
  },
  "generated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/assement/feedbacks/{user_id}
Obtener todos los feedbacks de un usuario.

**Path Parameters:**
- `user_id` (string): ID del usuario

**Query Parameters:**
- `skip` (int, optional): Número de elementos a omitir (default: 0)
- `limit` (int, optional): Número máximo de elementos (default: 10)

**Response:** `200 OK`
```json
{
  "feedbacks": [
    {
      "id": "feedback123",
      "skill_name": "JavaScript",
      "score": 85,
      "level": "intermediate",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### GET /api/v1/assement/feedback/assement/{feedback_id}
Obtener un feedback específico por ID.

**Path Parameters:**
- `feedback_id` (string): ID del feedback

**Response:** `200 OK`
```json
{
  "id": "feedback123",
  "session_id": "session123",
  "user_id": "user123",
  "skill_name": "JavaScript",
  "score": 85,
  "level": "intermediate",
  "detailed_feedback": {
    "strengths": ["Conceptos básicos"],
    "areas_for_improvement": ["Async/await"],
    "recommendations": ["Practicar promesas"]
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Códigos de Estado HTTP

- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado exitosamente
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error interno del servidor

## Despliegue

### Despliegue en EC2 con Docker

1. **Preparar instancia EC2:**
```bash
# Instalar Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
```

2. **Configurar Nginx como proxy reverso:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Ejecutar con Docker Compose:**
```bash
docker-compose up -d
```

### Integración con Kong API Gateway

Para agregar protección JWT y gestión de APIs con Kong:

1. **Crear servicio en Kong:**
```bash
curl -i -X POST http://kong:8001/services/ \
  --data "name=skill-assessment" \
  --data "url=http://skill-assessment-api:8000"
```

2. **Crear ruta:**
```bash
curl -i -X POST http://kong:8001/services/skill-assessment/routes \
  --data "hosts=your-domain.com" \
  --data "paths=/api"
```

3. **Agregar plugin JWT:**
```bash
curl -X POST http://kong:8001/services/skill-assessment/plugins \
  --data "name=jwt"
```

## Estructura del Proyecto

```
skillAssement/
├── docker-compose.yml          # Configuración de Docker Compose
├── Dockerfile                  # Imagen Docker
├── requirements.txt            # Dependencias Python
├── README.md                   # Documentación
└── src/
    ├── main.py                 # Punto de entrada de la aplicación
    ├── domain/                 # Capa de dominio
    │   ├── entities/           # Entidades del dominio
    │   ├── repositories/       # Interfaces de repositorios
    │   ├── services/          # Servicios del dominio
    │   └── value_objects/     # Objetos de valor
    ├── application/           # Capa de aplicación
    │   ├── dto/              # Data Transfer Objects
    │   ├── ports/            # Puertos de aplicación
    │   └── use_cases/        # Casos de uso
    ├── infrastructure/       # Capa de infraestructura
    │   ├── adapters/         # Adaptadores
    │   ├── config/           # Configuración
    │   ├── database/         # Conexión a base de datos
    │   ├── external_services/ # Servicios externos
    │   ├── messaging/        # Sistema de mensajería
    │   └── repositories/     # Implementaciones de repositorios
    └── presentation/         # Capa de presentación
        ├── api/              # Controladores de API
        ├── dependencies/     # Dependencias de FastAPI
        ├── middleware/       # Middleware personalizado
        └── schemas/          # Esquemas de validación
```

## Contribución

1. Fork el proyecto
2. Crear una rama para la nueva funcionalidad
3. Realizar commits con mensajes descriptivos
4. Crear Pull Request

## Licencia

Este proyecto está bajo la licencia MIT.
