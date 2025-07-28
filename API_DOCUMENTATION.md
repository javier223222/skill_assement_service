# Documentación de API - Microservicio Skill Assessment

## URL Base
```
https://teching.tech/skillassement
```

## Autenticación
Todos los endpoints requieren autenticación JWT a través del API Gateway Kong. Los tokens deben incluirse en el header `Authorization: Bearer <token>`.

---

## Endpoints de Habilidades (Skills)

### 1. Crear una nueva habilidad
**POST** `/skills/`

Crea una nueva habilidad en el sistema.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "name": "JavaScript",
  "description": "Conocimientos fundamentales de JavaScript para desarrollo web"
}
```

**Response:** `201 Created`
```json
{
  "id": "60d5ecb54f8a4c2d88c5e123",
  "name": "JavaScript",
  "description": "Conocimientos fundamentales de JavaScript para desarrollo web",
  "created_at": "2023-07-27T10:30:00Z",
  "updated_at": null
}
```

**Errores:**
- `422 Unprocessable Entity`: Error de validación en los datos
- `500 Internal Server Error`: Error interno del servidor

---

### 2. Obtener todas las habilidades
**GET** `/skills/skills/`

Obtiene una lista paginada de todas las habilidades disponibles.

**Query Parameters:**
- `skip` (int, opcional): Número de registros a omitir (default: 0)
- `limit` (int, opcional): Número máximo de registros a retornar (default: 10)

**Example Request:**
```
GET /skills/skills/?skip=0&limit=5
```

**Response:** `200 OK`
```json
{
  "total_skills": 25,
  "total_pages": 5,
  "has_next_page": true,
  "has_previous_page": false,
  "current_page": 1,
  "limit": 5,
  "skills": [
    {
      "id": "60d5ecb54f8a4c2d88c5e123",
      "name": "JavaScript",
      "description": "Conocimientos fundamentales de JavaScript para desarrollo web",
      "created_at": "2023-07-27T10:30:00Z",
      "updated_at": null
    },
    {
      "id": "60d5ecb54f8a4c2d88c5e124",
      "name": "Python",
      "description": "Programación en Python para ciencia de datos",
      "created_at": "2023-07-27T11:00:00Z",
      "updated_at": null
    }
  ]
}
```

**Errores:**
- `500 Internal Server Error`: Error interno del servidor

---

### 3. Obtener habilidad por ID
**GET** `/skills/{skill_id}`

Obtiene los detalles de una habilidad específica.

**Path Parameters:**
- `skill_id` (string): ID único de la habilidad

**Response:** `200 OK`
```json
{
  "id": "60d5ecb54f8a4c2d88c5e123",
  "name": "JavaScript",
  "description": "Conocimientos fundamentales de JavaScript para desarrollo web",
  "created_at": "2023-07-27T10:30:00Z",
  "updated_at": null
}
```

**Errores:**
- `404 Not Found`: Habilidad no encontrada
- `500 Internal Server Error`: Error interno del servidor

---

### 4. Actualizar una habilidad
**PATCH** `/skills/`

Actualiza los datos de una habilidad existente.

**Request Body:**
```json
{
  "id": "60d5ecb54f8a4c2d88c5e123",
  "name": "JavaScript Avanzado",
  "description": "Conocimientos avanzados de JavaScript incluyendo ES6+, async/await, y frameworks modernos",
  "created_at": "2023-07-27T10:30:00Z",
  "updated_at": "2023-07-27T12:00:00Z"
}
```

**Response:** `200 OK`
```json
{
  "id": "60d5ecb54f8a4c2d88c5e123",
  "name": "JavaScript Avanzado",
  "description": "Conocimientos avanzados de JavaScript incluyendo ES6+, async/await, y frameworks modernos",
  "created_at": "2023-07-27T10:30:00Z",
  "updated_at": "2023-07-27T12:00:00Z"
}
```

**Errores:**
- `404 Not Found`: Habilidad no encontrada
- `500 Internal Server Error`: Error interno del servidor

---

### 5. Eliminar una habilidad
**DELETE** `/skills/{skill_id}`

Elimina una habilidad del sistema junto con todas sus preguntas asociadas.

**Path Parameters:**
- `skill_id` (string): ID único de la habilidad

**Response:** `204 No Content`
```json
{
  "detail": "Skill deleted successfully"
}
```

**Errores:**
- `404 Not Found`: Habilidad no encontrada
- `500 Internal Server Error`: Error interno del servidor

---

## Endpoints de Evaluaciones (Assessments)

### 6. Iniciar una nueva evaluación
**POST** `/assement/{skill_id}`

Inicia una nueva sesión de evaluación para una habilidad específica.

**Path Parameters:**
- `skill_id` (string): ID único de la habilidad a evaluar

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
    "id": "session_456",
    "skill_id": "60d5ecb54f8a4c2d88c5e123",
    "user_id": "user123",
    "total_questions": 10,
    "current_question": 1,
    "is_finished": false,
    "answers": [],
    "created_at": "2023-07-27T13:00:00Z"
  },
  "next_step": 1
}
```

**Errores:**
- `422 Unprocessable Entity`: Error de validación
- `500 Internal Server Error`: Error interno del servidor

---

### 7. Obtener información de sesión
**GET** `/assement/session/{session_id}`

Obtiene los detalles completos de una sesión de evaluación.

**Path Parameters:**
- `session_id` (string): ID único de la sesión

**Response:** `200 OK`
```json
{
  "id": "session_456",
  "skill_id": "60d5ecb54f8a4c2d88c5e123",
  "user_id": "user123",
  "total_questions": 10,
  "current_question": 3,
  "is_finished": false,
  "answers": [
    {
      "id_question": 1,
      "answer": "const",
      "is_correct": true,
      "answered_at": "2023-07-27T13:05:00Z"
    },
    {
      "id_question": 2,
      "answer": "function declaration",
      "is_correct": false,
      "answered_at": "2023-07-27T13:07:00Z"
    }
  ],
  "created_at": "2023-07-27T13:00:00Z",
  "updated_at": "2023-07-27T13:07:00Z"
}
```

**Errores:**
- `404 Not Found`: Sesión no encontrada
- `500 Internal Server Error`: Error interno del servidor

---

### 8. Obtener pregunta específica
**GET** `/assement/questions/{id}`

Obtiene una pregunta específica de la evaluación.

**Path Parameters:**
- `id` (int): Número de la pregunta (1-10)

**Query Parameters:**
- `id_user` (string): ID del usuario
- `id_session` (string): ID de la sesión

**Example Request:**
```
GET /assement/questions/3?id_user=user123&id_session=session_456
```

**Response:** `200 OK`
```json
{
  "id": 3,
  "question_text": "¿Cuál es la diferencia entre 'let' y 'var' en JavaScript?",
  "options": [
    "No hay diferencia",
    "let tiene scope de bloque, var tiene scope de función",
    "var es más moderno que let",
    "let no puede ser redeclarado"
  ],
  "question_type": "multiple_choice",
  "difficulty": "medium",
  "points": 10
}
```

**Errores:**
- `404 Not Found`: Pregunta no encontrada
- `500 Internal Server Error`: Error interno del servidor

---

### 9. Responder una pregunta
**POST** `/assement/questions/{id_question}`

Envía la respuesta a una pregunta específica de la evaluación.

**Path Parameters:**
- `id_question` (int): Número de la pregunta

**Request Body:**
```json
{
  "id_session": "session_456",
  "id_user": "user123",
  "answer": "let tiene scope de bloque, var tiene scope de función"
}
```

**Response:** `201 Created`
```json
{
  "message": "Answer submitted successfully",
  "is_correct": true,
  "points_earned": 10,
  "next_question": 4,
  "total_questions": 10,
  "session_id": "session_456"
}
```

**Errores:**
- `422 Unprocessable Entity`: Error de validación
- `400 Bad Request`: Pregunta ya respondida o sesión finalizada
- `500 Internal Server Error`: Error interno del servidor

---

### 10. Actualizar respuesta de una pregunta
**PUT** `/assement/questions/{id_question}`

Actualiza la respuesta de una pregunta previamente respondida.

**Path Parameters:**
- `id_question` (int): Número de la pregunta

**Request Body:**
```json
{
  "id_session": "session_456",
  "id_user": "user123",
  "answer": "let no puede ser redeclarado"
}
```

**Response:** `200 OK`
```json
{
  "message": "Answer updated successfully",
  "is_correct": false,
  "points_earned": 0,
  "previous_points": 10,
  "session_id": "session_456"
}
```

**Errores:**
- `422 Unprocessable Entity`: Error de validación
- `404 Not Found`: Pregunta no encontrada
- `500 Internal Server Error`: Error interno del servidor

---

## Endpoints de Retroalimentación (Feedback)

### 11. Generar retroalimentación de evaluación
**GET** `/assement/feedback/{session_id}`

Genera y obtiene la retroalimentación completa de una evaluación finalizada.

**Path Parameters:**
- `session_id` (string): ID único de la sesión

**Response:** `200 OK`
```json
{
  "message": "Feedback generated successfully",
  "session_id": "session_456",
  "feedback": {
    "id": "feedback_789",
    "session_id": "session_456",
    "user_id": "user123",
    "skill_name": "JavaScript",
    "total_score": 75,
    "percentage": 75.0,
    "level_achieved": "Intermedio",
    "assessment_result": {
      "total_questions": 10,
      "correct_answers": 7,
      "incorrect_answers": 3,
      "total_points": 75,
      "max_points": 100
    },
    "relevant_skills_to_focus": [
      {
        "skill": "Closures en JavaScript",
        "importance": "high",
        "description": "Necesitas mejorar tu comprensión de closures"
      },
      {
        "skill": "Async/Await",
        "importance": "medium",
        "description": "Refuerza conceptos de programación asíncrona"
      }
    ],
    "recommended_tools_and_frameworks": [
      {
        "name": "MDN Web Docs",
        "type": "documentation",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "description": "Documentación oficial de JavaScript"
      },
      {
        "name": "JavaScript.info",
        "type": "tutorial",
        "url": "https://javascript.info/",
        "description": "Tutorial completo de JavaScript moderno"
      }
    ],
    "question_analysis": [
      {
        "question_id": 1,
        "was_correct": true,
        "user_answer": "const",
        "correct_answer": "const",
        "feedback": "Excelente, comprendes bien las declaraciones de variables"
      },
      {
        "question_id": 2,
        "was_correct": false,
        "user_answer": "function declaration",
        "correct_answer": "arrow function",
        "feedback": "Revisa las diferencias entre tipos de funciones en JavaScript"
      }
    ],
    "generated_at": "2023-07-27T13:30:00Z"
  }
}
```

**Errores:**
- `404 Not Found`: Sesión no encontrada
- `400 Bad Request`: La sesión no está completa para generar feedback
- `500 Internal Server Error`: Error interno del servidor

---

### 12. Obtener retroalimentaciones por usuario
**GET** `/assement/feedbacks/{user_id}`

Obtiene todas las retroalimentaciones de evaluaciones de un usuario específico.

**Path Parameters:**
- `user_id` (string): ID único del usuario

**Query Parameters:**
- `skip` (int, opcional): Número de registros a omitir (default: 0)
- `limit` (int, opcional): Número máximo de registros a retornar (default: 10)

**Example Request:**
```
GET /assement/feedbacks/user123?skip=0&limit=5
```

**Response:** `200 OK`
```json
{
  "user_id": "user123",
  "total_assessments": 15,
  "feedbacks": [
    {
      "feedback_id": "feedback_789",
      "skill_name": "JavaScript",
      "score": 75,
      "percentage": 75.0,
      "level_achieved": "Intermedio",
      "completed_at": "2023-07-27T13:30:00Z"
    },
    {
      "feedback_id": "feedback_790",
      "skill_name": "Python",
      "score": 90,
      "percentage": 90.0,
      "level_achieved": "Avanzado",
      "completed_at": "2023-07-26T10:15:00Z"
    }
  ],
  "pagination": {
    "skip": 0,
    "limit": 5,
    "total": 15,
    "has_more": true
  }
}
```

**Errores:**
- `404 Not Found`: Usuario no encontrado o sin evaluaciones
- `500 Internal Server Error`: Error interno del servidor

---

### 13. Obtener retroalimentación específica por ID
**GET** `/assement/feedback/assement/{feedback_id}`

Obtiene los detalles completos de una retroalimentación específica.

**Path Parameters:**
- `feedback_id` (string): ID único de la retroalimentación

**Response:** `200 OK`
```json
{
  "id": "feedback_789",
  "session_id": "session_456",
  "user_id": "user123",
  "skill_name": "JavaScript",
  "total_score": 75,
  "percentage": 75.0,
  "level_achieved": "Intermedio",
  "assessment_result": {
    "total_questions": 10,
    "correct_answers": 7,
    "incorrect_answers": 3,
    "total_points": 75,
    "max_points": 100
  },
  "relevant_skills_to_focus": [
    {
      "skill": "Closures en JavaScript",
      "importance": "high",
      "description": "Necesitas mejorar tu comprensión de closures"
    }
  ],
  "recommended_tools_and_frameworks": [
    {
      "name": "MDN Web Docs",
      "type": "documentation",
      "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
      "description": "Documentación oficial de JavaScript"
    }
  ],
  "question_analysis": [
    {
      "question_id": 1,
      "was_correct": true,
      "user_answer": "const",
      "correct_answer": "const",
      "feedback": "Excelente, comprendes bien las declaraciones de variables"
    }
  ],
  "generated_at": "2023-07-27T13:30:00Z"
}
```

**Errores:**
- `404 Not Found`: Retroalimentación no encontrada
- `500 Internal Server Error`: Error interno del servidor

---

## Códigos de Estado HTTP

### Códigos de Éxito
- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Recurso eliminado exitosamente

### Códigos de Error del Cliente
- `400 Bad Request`: Solicitud malformada o datos inválidos
- `401 Unauthorized`: Token de autenticación faltante o inválido
- `403 Forbidden`: Sin permisos para acceder al recurso
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación en los datos

### Códigos de Error del Servidor
- `500 Internal Server Error`: Error interno del servidor
- `503 Service Unavailable`: Servicio temporalmente no disponible

---

## Modelos de Datos

### Skill (Habilidad)
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### User Session (Sesión de Usuario)
```json
{
  "id": "string",
  "skill_id": "string",
  "user_id": "string",
  "total_questions": "integer",
  "current_question": "integer",
  "is_finished": "boolean",
  "answers": "array",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Assessment Feedback (Retroalimentación)
```json
{
  "id": "string",
  "session_id": "string",
  "user_id": "string",
  "skill_name": "string",
  "total_score": "integer",
  "percentage": "float",
  "level_achieved": "string",
  "assessment_result": "object",
  "relevant_skills_to_focus": "array",
  "recommended_tools_and_frameworks": "array",
  "question_analysis": "array",
  "generated_at": "datetime"
}
```

---

## Notas Importantes

1. **Autenticación**: Todos los endpoints requieren autenticación JWT válida
2. **Rate Limiting**: El API Gateway puede aplicar límites de velocidad
3. **Validación**: Todos los datos de entrada son validados automáticamente
4. **Paginación**: Los endpoints que retornan listas incluyen paginación
5. **Timestamps**: Todas las fechas están en formato ISO 8601 UTC
6. **IDs**: Todos los identificadores son strings únicos (ObjectId de MongoDB)

---

## Ejemplos de Uso

### Flujo Completo de Evaluación

1. **Crear una habilidad:**
```bash
POST /skills/
{
  "name": "React",
  "description": "Framework de JavaScript para interfaces de usuario"
}
```

2. **Iniciar evaluación:**
```bash
POST /assement/60d5ecb54f8a4c2d88c5e123
{
  "id_user": "user123"
}
```

3. **Obtener primera pregunta:**
```bash
GET /assement/questions/1?id_user=user123&id_session=session_456
```

4. **Responder pregunta:**
```bash
POST /assement/questions/1
{
  "id_session": "session_456",
  "id_user": "user123",
  "answer": "useState"
}
```

5. **Obtener retroalimentación:**
```bash
GET /assement/feedback/session_456
```

Este flujo se repite para todas las preguntas hasta completar la evaluación.
