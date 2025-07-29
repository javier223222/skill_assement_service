# Refactorización DDD - Domain-Driven Design

## Análisis de la Estructura Actual

### Estructura Actual
```
src/
├── application/          # Capa de Aplicación (Use Cases)
├── domain/              # Capa de Dominio (Entidades, Value Objects, Repositories)
├── infrastructure/      # Capa de Infraestructura (Adaptadores, DB, Servicios Externos)
├── presentation/        # Capa de Presentación (Controllers, API)
└── main.py             # Punto de entrada
```

### Problemas Identificados
1. **Falta de separación clara de contextos limitados (Bounded Contexts)**
2. **Ausencia de Domain Services**
3. **Repositories mezclados entre dominio e infraestructura**
4. **Falta de Aggregates bien definidos**
5. **Value Objects insuficientes**
6. **Domain Events no implementados**
7. **Falta de Factory patterns**

## Nueva Estructura DDD Propuesta

```
src/
├── shared/                           # Shared Kernel
│   ├── domain/
│   │   ├── entities/
│   │   │   └── base_entity.py
│   │   ├── value_objects/
│   │   │   └── base_value_object.py
│   │   ├── events/
│   │   │   ├── domain_event.py
│   │   │   └── event_dispatcher.py
│   │   └── exceptions/
│   │       └── domain_exceptions.py
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   └── base_repository.py
│   │   └── messaging/
│   └── application/
│       └── base_use_case.py
│
├── skill_management/                 # Bounded Context: Gestión de Skills
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── skill.py
│   │   │   └── skill_category.py
│   │   ├── value_objects/
│   │   │   ├── skill_name.py
│   │   │   ├── skill_description.py
│   │   │   └── difficulty_level.py
│   │   ├── repositories/
│   │   │   └── skill_repository.py
│   │   ├── services/
│   │   │   └── skill_domain_service.py
│   │   ├── events/
│   │   │   ├── skill_created.py
│   │   │   └── skill_updated.py
│   │   └── factories/
│   │       └── skill_factory.py
│   ├── application/
│   │   ├── commands/
│   │   │   ├── create_skill_command.py
│   │   │   ├── update_skill_command.py
│   │   │   └── delete_skill_command.py
│   │   ├── queries/
│   │   │   ├── get_skill_query.py
│   │   │   └── get_all_skills_query.py
│   │   ├── handlers/
│   │   │   ├── create_skill_handler.py
│   │   │   ├── update_skill_handler.py
│   │   │   └── get_skill_handler.py
│   │   └── dto/
│   │       └── skill_dto.py
│   └── infrastructure/
│       ├── persistence/
│       │   └── mongo_skill_repository.py
│       └── external_services/
│
├── assessment/                       # Bounded Context: Evaluaciones
│   ├── domain/
│   │   ├── aggregates/
│   │   │   ├── assessment.py        # Aggregate Root
│   │   │   └── question_set.py
│   │   ├── entities/
│   │   │   ├── question.py
│   │   │   ├── user_session.py
│   │   │   └── answer.py
│   │   ├── value_objects/
│   │   │   ├── question_number.py
│   │   │   ├── question_text.py
│   │   │   ├── answer_option.py
│   │   │   ├── correct_answer.py
│   │   │   └── session_id.py
│   │   ├── repositories/
│   │   │   ├── assessment_repository.py
│   │   │   ├── question_repository.py
│   │   │   └── user_session_repository.py
│   │   ├── services/
│   │   │   ├── assessment_generator_service.py
│   │   │   ├── scoring_service.py
│   │   │   └── validation_service.py
│   │   ├── events/
│   │   │   ├── assessment_created.py
│   │   │   ├── question_answered.py
│   │   │   └── assessment_completed.py
│   │   └── factories/
│   │       ├── assessment_factory.py
│   │       └── question_factory.py
│   ├── application/
│   │   ├── commands/
│   │   │   ├── create_assessment_command.py
│   │   │   ├── answer_question_command.py
│   │   │   └── complete_assessment_command.py
│   │   ├── queries/
│   │   │   ├── get_assessment_query.py
│   │   │   ├── get_question_query.py
│   │   │   └── get_session_query.py
│   │   ├── handlers/
│   │   │   ├── create_assessment_handler.py
│   │   │   ├── answer_question_handler.py
│   │   │   └── get_question_handler.py
│   │   └── dto/
│   │       ├── assessment_dto.py
│   │       ├── question_dto.py
│   │       └── answer_dto.py
│   └── infrastructure/
│       ├── persistence/
│       │   ├── mongo_assessment_repository.py
│       │   ├── mongo_question_repository.py
│       │   └── mongo_session_repository.py
│       └── external_services/
│           └── gemini_service.py
│
├── feedback/                         # Bounded Context: Retroalimentación
│   ├── domain/
│   │   ├── aggregates/
│   │   │   └── assessment_feedback.py
│   │   ├── entities/
│   │   │   ├── feedback_report.py
│   │   │   └── recommendation.py
│   │   ├── value_objects/
│   │   │   ├── score.py
│   │   │   ├── percentage.py
│   │   │   └── feedback_text.py
│   │   ├── repositories/
│   │   │   └── feedback_repository.py
│   │   ├── services/
│   │   │   ├── feedback_generator_service.py
│   │   │   └── analytics_service.py
│   │   ├── events/
│   │   │   └── feedback_generated.py
│   │   └── factories/
│   │       └── feedback_factory.py
│   ├── application/
│   │   ├── commands/
│   │   │   └── generate_feedback_command.py
│   │   ├── queries/
│   │   │   ├── get_feedback_query.py
│   │   │   └── get_user_feedbacks_query.py
│   │   ├── handlers/
│   │   │   ├── generate_feedback_handler.py
│   │   │   └── get_feedback_handler.py
│   │   └── dto/
│   │       └── feedback_dto.py
│   └── infrastructure/
│       └── persistence/
│           └── mongo_feedback_repository.py
│
├── presentation/                     # Unified Presentation Layer
│   ├── api/
│   │   ├── controllers/
│   │   │   ├── skill_controller.py
│   │   │   ├── assessment_controller.py
│   │   │   └── feedback_controller.py
│   │   ├── middlewares/
│   │   │   ├── authentication_middleware.py
│   │   │   ├── validation_middleware.py
│   │   │   └── error_handler_middleware.py
│   │   └── schemas/
│   │       ├── skill_schemas.py
│   │       ├── assessment_schemas.py
│   │       └── feedback_schemas.py
│   └── dependency_injection/
│       ├── container.py
│       └── modules/
│           ├── skill_module.py
│           ├── assessment_module.py
│           └── feedback_module.py
│
├── infrastructure/                   # Cross-cutting Infrastructure
│   ├── persistence/
│   │   ├── mongo/
│   │   │   ├── connection.py
│   │   │   └── unit_of_work.py
│   │   └── configuration/
│   ├── messaging/
│   │   ├── rabbitmq/
│   │   └── event_bus.py
│   ├── external_services/
│   │   ├── ai_services/
│   │   └── notification_services/
│   ├── security/
│   │   ├── authentication/
│   │   ├── authorization/
│   │   └── validation/
│   └── configuration/
│       ├── app_config.py
│       └── environment_config.py
│
└── main.py                          # Application Entry Point
```

## Principios DDD Aplicados

### 1. Bounded Contexts
- **Skill Management**: Gestión de habilidades y categorías
- **Assessment**: Creación y ejecución de evaluaciones
- **Feedback**: Generación y consulta de retroalimentación

### 2. Aggregates y Aggregate Roots
- **Assessment Aggregate**: Maneja la consistencia de evaluaciones, preguntas y respuestas
- **Skill Aggregate**: Gestiona habilidades y sus categorías
- **Feedback Aggregate**: Controla la retroalimentación y recomendaciones

### 3. Value Objects
- Encapsulan lógica de validación y comportamiento
- Inmutables y sin identidad
- Aportan expresividad al modelo

### 4. Domain Services
- Lógica de dominio que no pertenece a ninguna entidad específica
- Orquestación de operaciones complejas
- Servicios puros sin efectos secundarios

### 5. Domain Events
- Comunicación entre contextos limitados
- Desacoplamiento temporal
- Auditabilidad y trazabilidad

### 6. CQRS (Command Query Responsibility Segregation)
- Separación clara entre comandos y consultas
- Optimización específica para lectura y escritura
- Escalabilidad mejorada

## Beneficios de la Refactorización

1. **Mantenibilidad**: Código más organizado y fácil de mantener
2. **Escalabilidad**: Cada contexto puede evolucionar independientemente
3. **Testabilidad**: Aislamiento de responsabilidades facilita testing
4. **Expresividad**: El código refleja mejor el dominio del negocio
5. **Flexibilidad**: Fácil adaptación a cambios de requisitos
6. **Reusabilidad**: Componentes bien definidos y reutilizables

## Plan de Migración

### Fase 1: Shared Kernel
1. Crear abstracciones base
2. Implementar Domain Events
3. Configurar infraestructura compartida

### Fase 2: Skill Management Context
1. Migrar entidad Skill
2. Crear Value Objects
3. Implementar Repository pattern
4. Crear Domain Services

### Fase 3: Assessment Context
1. Refactorizar Assessment como Aggregate
2. Crear Question y UserSession entities
3. Implementar Value Objects específicos
4. Migrar Use Cases a Handlers

### Fase 4: Feedback Context
1. Crear Feedback Aggregate
2. Implementar servicios de análisis
3. Migrar generación de retroalimentación

### Fase 5: Presentation Layer
1. Refactorizar controllers
2. Implementar dependency injection
3. Crear schemas específicos por contexto

### Fase 6: Infrastructure
1. Implementar Unit of Work pattern
2. Configurar Event Bus
3. Optimizar persistencia por contexto
