# Guía de Integración - Microservicio Skill Assessment para Flutter

## Información General del Servicio

### URL Base
```
https://teching.tech/skillassement/api/v1/
```

### Autenticación
**OBLIGATORIO**: Todos los endpoints requieren autenticación Bearer Token en el header:
```
Authorization: Bearer <your_jwt_token>
```

### Arquitectura del Servicio
- **Framework**: FastAPI
- **Base de Datos**: MongoDB con Beanie ODM
- **API Gateway**: Kong
- **Generación de Preguntas**: Google Gemini AI
- **Mensajería**: RabbitMQ para procesamiento asíncrono

---

## Modelos de Datos (Dart Classes para Flutter)

### 1. Skill Model
```dart
class Skill {
  final String id;
  final String name;
  final String? description;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Skill({
    required this.id,
    required this.name,
    this.description,
    required this.createdAt,
    this.updatedAt,
  });

  factory Skill.fromJson(Map<String, dynamic> json) {
    return Skill(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null 
        ? DateTime.parse(json['updated_at']) 
        : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
}
```

### 2. User Session Model
```dart
class AnswerSessionModel {
  final int idQuestion;
  final String answer;

  AnswerSessionModel({
    required this.idQuestion,
    required this.answer,
  });

  factory AnswerSessionModel.fromJson(Map<String, dynamic> json) {
    return AnswerSessionModel(
      idQuestion: json['id_question'],
      answer: json['answer'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id_question': idQuestion,
      'answer': answer,
    };
  }
}

class UserSession {
  final String id;
  final String userId;
  final String skillId;
  final List<AnswerSessionModel> answers;
  final DateTime createdAt;
  final int totalQuestions;
  final double? percentage;
  final bool isFinished;
  final int actualNumberOfQuestions;
  final DateTime? finishedAt;
  final String status; // "in_progress", "completed", "abandoned"
  final DateTime updatedAt;

  UserSession({
    required this.id,
    required this.userId,
    required this.skillId,
    required this.answers,
    required this.createdAt,
    required this.totalQuestions,
    this.percentage,
    required this.isFinished,
    required this.actualNumberOfQuestions,
    this.finishedAt,
    required this.status,
    required this.updatedAt,
  });

  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      id: json['id'],
      userId: json['user_id'],
      skillId: json['skill_id'],
      answers: (json['answers'] as List)
          .map((e) => AnswerSessionModel.fromJson(e))
          .toList(),
      createdAt: DateTime.parse(json['created_at']),
      totalQuestions: json['total_questions'],
      percentage: json['percentage']?.toDouble(),
      isFinished: json['is_finished'],
      actualNumberOfQuestions: json['actual_number_of_questions'],
      finishedAt: json['finished_at'] != null 
        ? DateTime.parse(json['finished_at']) 
        : null,
      status: json['status'],
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}
```

### 3. Question Model
```dart
class Question {
  final String id; // MongoDB ObjectId
  final int questionNumber; // Número secuencial: 1, 2, 3, etc.
  final String skillId;
  final String subcategory;
  final String type;
  final String question;
  final List<String> options;
  final String correctAnswer;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final List<String>? recommendedTools;

  Question({
    required this.id,
    required this.questionNumber,
    required this.skillId,
    required this.subcategory,
    required this.type,
    required this.question,
    required this.options,
    required this.correctAnswer,
    required this.createdAt,
    this.updatedAt,
    this.recommendedTools,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['_id'] ?? json['id'], // MongoDB ObjectId
      questionNumber: json['question_number'],
      skillId: json['skillid'],
      subcategory: json['subcategory'],
      type: json['type'],
      question: json['question'],
      options: List<String>.from(json['options']),
      correctAnswer: json['correct_answer'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null 
        ? DateTime.parse(json['updated_at']) 
        : null,
      recommendedTools: json['recommended_tools'] != null 
        ? List<String>.from(json['recommended_tools']) 
        : null,
    );
  }
}
```

### 4. Assessment Feedback Model
```dart
class UserAnswer {
  final String answer;
  final bool isCorrect;

  UserAnswer({required this.answer, required this.isCorrect});

  factory UserAnswer.fromJson(Map<String, dynamic> json) {
    return UserAnswer(
      answer: json['answer'],
      isCorrect: json['is_correct'],
    );
  }
}

class QuestionAnalysis {
  final int questionNumber;  // Cambio de questionId a questionNumber
  final String question;
  final String subcategory;
  final String correctAnswer;
  final List<UserAnswer> userAnswers;

  QuestionAnalysis({
    required this.questionNumber,  // Cambio de questionId a questionNumber
    required this.question,
    required this.subcategory,
    required this.correctAnswer,
    required this.userAnswers,
  });

  factory QuestionAnalysis.fromJson(Map<String, dynamic> json) {
    return QuestionAnalysis(
      questionNumber: json['question_number'],  // Cambio de question_id a question_number
      question: json['question'],
      subcategory: json['subcategory'],
      correctAnswer: json['correct_answer'],
      userAnswers: (json['user_answers'] as List)
          .map((e) => UserAnswer.fromJson(e))
          .toList(),
    );
  }
}

class AssessmentResult {
  final String subcategory;
  final double percentage;

  AssessmentResult({required this.subcategory, required this.percentage});

  factory AssessmentResult.fromJson(Map<String, dynamic> json) {
    return AssessmentResult(
      subcategory: json['subcategory'],
      percentage: json['percentage'].toDouble(),
    );
  }
}

class RelevantSkillToFocusOn {
  final String skill;
  final double score;

  RelevantSkillToFocusOn({required this.skill, required this.score});

  factory RelevantSkillToFocusOn.fromJson(Map<String, dynamic> json) {
    return RelevantSkillToFocusOn(
      skill: json['skill'],
      score: json['score'].toDouble(),
    );
  }
}

class RecommendedToolsAndFrameworks {
  final String name;

  RecommendedToolsAndFrameworks({required this.name});

  factory RecommendedToolsAndFrameworks.fromJson(Map<String, dynamic> json) {
    return RecommendedToolsAndFrameworks(name: json['name']);
  }
}

class AssessmentFeedback {
  final String id;
  final String userId;
  final String sessionId;
  final double assessmentResult;
  final double industryAverage;
  final double pointsEarned;
  final DateTime createdAt;
  final List<AssessmentResult> results;
  final List<RelevantSkillToFocusOn> relevantSkills;
  final List<RecommendedToolsAndFrameworks> recommendedTools;
  final List<QuestionAnalysis> questionsAnalysis;
  final double goodAnswers;
  final double badAnswers;

  AssessmentFeedback({
    required this.id,
    required this.userId,
    required this.sessionId,
    required this.assessmentResult,
    required this.industryAverage,
    required this.pointsEarned,
    required this.createdAt,
    required this.results,
    required this.relevantSkills,
    required this.recommendedTools,
    required this.questionsAnalysis,
    required this.goodAnswers,
    required this.badAnswers,
  });

  factory AssessmentFeedback.fromJson(Map<String, dynamic> json) {
    return AssessmentFeedback(
      id: json['id'],
      userId: json['user_id'],
      sessionId: json['session_id'],
      assessmentResult: json['assement_result'].toDouble(),
      industryAverage: json['industry_avarage'].toDouble(),
      pointsEarned: json['points_earned'].toDouble(),
      createdAt: DateTime.parse(json['created_at']),
      results: (json['results'] as List)
          .map((e) => AssessmentResult.fromJson(e))
          .toList(),
      relevantSkills: (json['relevant_skills'] as List)
          .map((e) => RelevantSkillToFocusOn.fromJson(e))
          .toList(),
      recommendedTools: (json['recommended_tools'] as List)
          .map((e) => RecommendedToolsAndFrameworks.fromJson(e))
          .toList(),
      questionsAnalysis: (json['questions_analysis'] as List)
          .map((e) => QuestionAnalysis.fromJson(e))
          .toList(),
      goodAnswers: json['good_answers'].toDouble(),
      badAnswers: json['bad_answers'].toDouble(),
    );
  }
}
```

---

## Endpoints del API

### 1. Health Check
**GET** `/`

Verificar estado del servicio.

**Response:** `200 OK`
```json
{
  "status": "ok",
  "service": "skill-assessment-service",
  "message": "Servicio funcionando correctamente"
}
```

---

## Gestión de Habilidades (Skills)

### 2. Crear Habilidad
**POST** `/skills/`

**Request Body:**
```json
{
  "name": "JavaScript",
  "description": "Conocimientos fundamentales de JavaScript"
}
```

**Reglas de Validación:**
- `name`: String requerido, no vacío
- `description`: String requerido, no vacío

**Response:** `201 Created`
```json
{
  "id": "60d5ecb54f8a4c2d88c5e123",
  "name": "JavaScript",
  "description": "Conocimientos fundamentales de JavaScript",
  "created_at": "2023-07-27T10:30:00.000Z",
  "updated_at": null
}
```

### 3. Obtener Todas las Habilidades
**GET** `/skills/skills/`

**Query Parameters:**
- `skip` (int, opcional): Default 0
- `limit` (int, opcional): Default 10, máximo recomendado 50

**Response:** `200 OK`
```json
{
  "total_skills": 25,
  "total_pages": 3,
  "has_next_page": true,
  "has_previous_page": false,
  "current_page": 1,
  "limit": 10,
  "skills": [
    {
      "id": "60d5ecb54f8a4c2d88c5e123",
      "name": "JavaScript",
      "description": "Conocimientos fundamentales de JavaScript",
      "created_at": "2023-07-27T10:30:00.000Z",
      "updated_at": null
    }
  ]
}
```

### 4. Obtener Habilidad por ID
**GET** `/skills/{skill_id}`

**Path Parameters:**
- `skill_id`: String (MongoDB ObjectId)

**Response:** `200 OK`
```json
{
  "id": "60d5ecb54f8a4c2d88c5e123",
  "name": "JavaScript",
  "description": "Conocimientos fundamentales de JavaScript",
  "created_at": "2023-07-27T10:30:00.000Z",
  "updated_at": null
}
```

**Errores:**
- `404`: Habilidad no encontrada

### 5. Actualizar Habilidad
**PATCH** `/skills/`

**Request Body:** (Enviar objeto Skill completo)
```json
{
  "id": "60d5ecb54f8a4c2d88c5e123",
  "name": "JavaScript Avanzado",
  "description": "Conocimientos avanzados de JavaScript",
  "created_at": "2023-07-27T10:30:00.000Z",
  "updated_at": "2023-07-27T12:00:00.000Z"
}
```

**Response:** `200 OK` (mismo formato que crear)

### 6. Eliminar Habilidad
**DELETE** `/skills/{skill_id}`

**Response:** `204 No Content`
```json
{
  "detail": "Skill deleted successfully"
}
```

**Reglas de Negocio:**
- Elimina la habilidad y TODAS las preguntas asociadas
- Operación irreversible

---

## Gestión de Evaluaciones (Assessments)

### 7. Iniciar Nueva Evaluación
**POST** `/assement/{skill_id}`

Genera una nueva sesión de evaluación con preguntas generadas por IA.

**Path Parameters:**
- `skill_id`: String (ID de la habilidad a evaluar)

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
    "user_id": "user123",
    "skill_id": "60d5ecb54f8a4c2d88c5e123",
    "answers": [],
    "created_at": "2023-07-27T13:00:00.000Z",
    "total_questions": 10,
    "percentage": null,
    "is_finished": false,
    "actual_number_of_questions": 0,
    "finished_at": null,
    "status": "in_progress",
    "updated_at": "2023-07-27T13:00:00.000Z"
  },
  "next_step": 1
}
```

**Reglas de Negocio:**
- Se generan automáticamente 10 preguntas por evaluación
- Cada evaluación es única por usuario/habilidad/sesión
- El tiempo de generación puede tomar 5-15 segundos (IA)

### 8. Obtener Información de Sesión
**GET** `/assement/session/{session_id}`

**Path Parameters:**
- `session_id`: String (ID de la sesión)

**Response:** `200 OK`
```json
{
  "id": "session_456",
  "user_id": "user123",
  "skill_id": "60d5ecb54f8a4c2d88c5e123",
  "answers": [
    {
      "id_question": 1,
      "answer": "const"
    }
  ],
  "created_at": "2023-07-27T13:00:00.000Z",
  "total_questions": 10,
  "percentage": null,
  "is_finished": false,
  "actual_number_of_questions": 1,
  "finished_at": null,
  "status": "in_progress",
  "updated_at": "2023-07-27T13:05:00.000Z"
}
```

### 9. Obtener Pregunta Específica
**GET** `/assement/questions/{id}`

**Path Parameters:**
- `id`: int (Número de pregunta 1-10)

**Query Parameters:**
- `id_user`: String (ID del usuario)
- `id_session`: String (ID de la sesión)

**Example Request:**
```
GET /assement/questions/3?id_user=user123&id_session=session_456
```

**Response:** `200 OK`
```json
{
  "id": 3,
  "text": "¿Cuál es la diferencia entre 'let' y 'var' en JavaScript?",
  "options": [
    "No hay diferencia",
    "let tiene scope de bloque, var tiene scope de función",
    "var es más moderno que let",
    "let no puede ser redeclarado"
  ],
  "subcategory": "Variables y Tipos",
  "type": "multiple_choice",
  "recommended_tools": ["MDN Web Docs", "JavaScript.info"],
  "has_next": true,
  "has_previous": true,
  "next_question_id": 4
}
```

**Reglas de Negocio:**
- Solo devuelve la pregunta en formato simplificado para el usuario
- Debe validarse que el usuario tenga acceso a esa sesión
- Las preguntas son secuenciales 1-10 por cada skill
- El campo `id` corresponde al número de pregunta (1, 2, 3, etc.)

### 10. Responder Pregunta
**POST** `/assement/questions/{id_question}`

**Path Parameters:**
- `id_question`: int (Número de pregunta)

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
  "message": "Answer recorded successfully",
  "session_id": "session_456",
  "question_answered": 3,
  "total_questions": 10,
  "questions_answered": 3,
  "is_completed": false,
  "next_question": 4
}
```

**Reglas de Negocio:**
- NO se valida si la respuesta es correcta en tiempo real
- Una pregunta solo puede ser respondida una vez (usar PUT para actualizar)
- La sesión debe estar en estado "in_progress"
- Debe ser el usuario propietario de la sesión

### 11. Actualizar Respuesta
**PUT** `/assement/questions/{id_question}`

Permite cambiar una respuesta ya enviada.

**Mismo formato que POST**

**Response:** `200 OK`
```json
{
  "message": "Answer updated successfully",
  "session_id": "session_456",
  "question_id": 3,
  "previous_answer": "No hay diferencia",
  "new_answer": "let tiene scope de bloque, var tiene scope de función",
  "update_successful": true
}
```

---

## Gestión de Retroalimentación (Feedback)

### 12. Generar/Obtener Retroalimentación
**GET** `/assement/feedback/{session_id}`

Genera la retroalimentación de una evaluación completada o la devuelve si ya existe.

**Path Parameters:**
- `session_id`: String

**Response:** `200 OK`
```json
{
  "message": "Feedback generated successfully",
  "session_id": "session_456",
  "feedback": {
    "id": "feedback_789",
    "user_id": "user123",
    "session_id": "session_456",
    "assement_result": 75.0,
    "industry_avarage": 68.5,
    "points_earned": 75.0,
    "created_at": "2023-07-27T13:30:00.000Z",
    "results": [
      {
        "subcategory": "Variables y Tipos",
        "percentage": 80.0
      },
      {
        "subcategory": "Funciones",
        "percentage": 70.0
      }
    ],
    "relevant_skills": [
      {
        "skill": "Closures en JavaScript",
        "score": 60.0
      }
    ],
    "recommended_tools": [
      {
        "name": "MDN Web Docs"
      },
      {
        "name": "JavaScript.info"
      }
    ],
    "questions_analysis": [
      {
        "question_id": 1,
        "question": "¿Qué palabra clave se usa para declarar constantes?",
        "subcategory": "Variables y Tipos",
        "correct_answer": "const",
        "user_answers": [
          {
            "answer": "const",
            "is_correct": true
          }
        ]
      }
    ],
    "good_answers": 7.0,
    "bad_answers": 3.0
  }
}
```

**Reglas de Negocio:**
- Solo se puede generar si la sesión tiene las 10 preguntas respondidas
- Si ya existe feedback para la sesión, lo retorna directamente
- El procesamiento con IA puede tomar 10-30 segundos
- Se envía notificación asíncrona vía RabbitMQ

### 13. Obtener Retroalimentaciones por Usuario
**GET** `/assement/feedbacks/{user_id}`

**Path Parameters:**
- `user_id`: String

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 10)

**Response:** `200 OK`
```json
{
  "user_id": "user123",
  "total_feedbacks": 5,
  "feedbacks": [
    {
      "feedback_id": "feedback_789",
      "session_id": "session_456",
      "skill_name": "JavaScript",
      "score": 75.0,
      "completed_at": "2023-07-27T13:30:00.000Z"
    }
  ],
  "pagination": {
    "skip": 0,
    "limit": 10,
    "has_more": false
  }
}
```

### 14. Obtener Retroalimentación Específica
**GET** `/assement/feedback/assement/{feedback_id}`

**Path Parameters:**
- `feedback_id`: String

**Response:** `200 OK` (mismo formato que generar feedback)

---

## Flujo Completo de Evaluación

### 1. Flujo Principal
```
1. Obtener habilidades disponibles
   GET /skills/skills/

2. Seleccionar habilidad e iniciar evaluación
   POST /assement/{skill_id}
   Body: {"id_user": "user123"}

3. Para cada pregunta (1-10):
   a. Obtener pregunta
      GET /assement/questions/{question_number}?id_user=user123&id_session=session_id
   
   b. Mostrar pregunta al usuario
   
   c. Enviar respuesta
      POST /assement/questions/{question_number}
      Body: {"id_session": "session_id", "id_user": "user123", "answer": "respuesta"}

4. Después de 10 preguntas, generar feedback
   GET /assement/feedback/{session_id}

5. Mostrar resultados al usuario
```

### 2. Flujo de Actualización de Respuesta
```
1. Usuario quiere cambiar respuesta
   PUT /assement/questions/{question_number}
   Body: {"id_session": "session_id", "id_user": "user123", "answer": "nueva_respuesta"}

2. Regenerar feedback si es necesario
   GET /assement/feedback/{session_id}
```

### 3. Flujo de Historial
```
1. Obtener todas las evaluaciones del usuario
   GET /assement/feedbacks/{user_id}

2. Ver detalle de evaluación específica
   GET /assement/feedback/assement/{feedback_id}
```

---

## Manejo de Errores

### Códigos de Estado HTTP
- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado
- `204 No Content`: Eliminación exitosa
- `400 Bad Request`: Datos inválidos
- `401 Unauthorized`: Token inválido/ausente
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación
- `500 Internal Server Error`: Error del servidor

### Estructura de Error
```json
{
  "detail": "Descripción específica del error"
}
```

### Errores Comunes de Validación
1. **Token ausente/inválido**: Verificar header Authorization
2. **Session no encontrada**: Verificar ID de sesión
3. **Usuario no autorizado**: Verificar propiedad de sesión
4. **Pregunta ya respondida**: Usar PUT en lugar de POST
5. **Evaluación no completada**: Responder todas las preguntas antes del feedback
6. **Error de IDs duplicados**: Si ves `E11000 duplicate key error`, contacta al equipo de backend para limpiar la base de datos

---

## Implementación en Flutter

### 1. Servicio HTTP Base
```dart
class SkillAssessmentService {
  static const String baseUrl = 'https://teching.tech/skillassement/api/v1';
  final String token;

  SkillAssessmentService({required this.token});

  Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $token',
  };

  // Implementar métodos HTTP aquí
}
```

### 2. Estados de la Aplicación
```dart
enum AssessmentState {
  notStarted,
  inProgress,
  completed,
  error
}

enum SessionStatus {
  inProgress,
  completed,
  abandoned
}
```

### 3. Validaciones del Cliente
- Validar token antes de cada request
- Verificar conectividad de red
- Manejar timeouts (especialmente para generación de preguntas/feedback)
- Implementar retry logic para operaciones críticas
- Cachear respuestas para experiencia offline limitada

---

## Consideraciones de Rendimiento

### 1. Operaciones Costosas
- **Generar evaluación**: 5-15 segundos (IA)
- **Generar feedback**: 10-30 segundos (IA)
- **Consultas normales**: <1 segundo

### 2. Recomendaciones
- Mostrar loading indicators para operaciones de IA
- Implementar timeout de 45 segundos para generación
- Usar paginación para listas grandes
- Cachear habilidades disponibles
- Prefetch siguiente pregunta mientras usuario responde actual

### 3. Límites del Sistema
- Máximo 50 skills por request (usar paginación)
- 10 preguntas por evaluación (fijo)
- Timeout de generación: 45 segundos
- Rate limiting aplicado por Kong (configurar retry con backoff)

---

## Reglas de Negocio Críticas

### 1. Integridad de Sesión
- Un usuario solo puede tener una sesión activa por habilidad
- Las sesiones expiran después de 24 horas de inactividad
- No se puede modificar una sesión completada

### 2. Secuencia de Preguntas
- Las preguntas deben responderse en orden secuencial (1, 2, 3, etc.)
- No se puede acceder a pregunta N+1 sin responder pregunta N
- Total fijo de 10 preguntas por evaluación
- Cada pregunta tiene un `question_number` único por skill

### 3. Generación de Feedback
- Requiere todas las 10 preguntas respondidas
- Se genera una sola vez por sesión
- Incluye análisis con IA de Google Gemini

### 4. Autenticación y Autorización
- Todos los endpoints requieren JWT válido
- Los usuarios solo pueden acceder a sus propias sesiones
- No hay roles administrativos en este microservicio

Este documento proporciona toda la información necesaria para una integración completa y correcta con Flutter.
