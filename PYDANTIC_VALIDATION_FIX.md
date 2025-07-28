# Fix para Error de Validación Pydantic en Evaluaciones

## Problema Identificado

El error de validación Pydantic se debía a datos residuales en MongoDB con formato incorrecto:

```json
{
  "detail": "Error evaluating skill assessment: 2 validation errors for Question\n_id\n  Value error, Id must be of type PydanticObjectId [type=value_error, input_value=1, input_type=int]\nquestion_number\n  Field required [type=missing, input_value={'_id': 1, 'skillid': '68...ecommended_tools': None}, input_type=dict]"
}
```

## Causa Raíz

1. **Datos Residuales**: Existían documentos en MongoDB con `_id` numérico (1, 2, 3) en lugar de ObjectId
2. **Migración Incompleta**: El script de migración no había procesado correctamente todos los registros
3. **Conflicto de Esquemas**: Los datos antiguos no coincidían con el nuevo modelo Pydantic

## Solución Implementada

### 1. Limpieza Completa de Base de Datos

Se creó el script `scripts/clean_database.py` que:
- Elimina todas las preguntas con formato incorrecto
- Limpia sesiones de usuario residuales  
- Remueve feedbacks inconsistentes
- Permite empezar con datos limpios

### 2. Modelo Question Corregido

El modelo actual en `src/domain/entities/question.py` está correctamente configurado:

```python
class Question(Document):
    question_number: int = Field(..., index=True, description="Sequential number of the question (1, 2, 3, etc.)")
    skillid: str = Field(index=True, description="The ID of the skill associated with the question")
    # ... otros campos
    
    class Settings:
        collection = "questions"
        indexes = [
            [("skillid", 1), ("question_number", 1)],  # Índice compuesto
        ]
```

### 3. Repositorio Question Actualizado

El repositorio `src/domain/repositories/question_repository.py` maneja correctamente:
- Creación con `question_number` secuencial
- Búsquedas por `skillid` y `question_number`
- Validación automática de Pydantic

## Archivos Modificados

### Scripts de Utilidad
- `scripts/clean_database.py` - Limpieza completa de base de datos
- `scripts/check_questions_structure.py` - Verificación de estructura de datos
- `scripts/migrate_to_sequential_numbers.py` - Migración de datos (ya no necesario)

### Entidades y Repositorios
- `src/domain/entities/question.py` - Modelo corregido con question_number
- `src/domain/repositories/question_repository.py` - Métodos actualizados

### Casos de Uso
- `src/application/use_cases/create_assement_use_case.py` - Creación con question_number
- `src/application/use_cases/answer_question_use_case.py` - Acceso por question_number
- `src/application/use_cases/evaluate_skill_assement_use_case.py` - Evaluación corregida

## Pasos para Probar

### 1. Verificar Estado Actual
```bash
python scripts/check_questions_structure.py
```

### 2. Crear Nueva Evaluación
```bash
# POST /api/v1/assessments/create
{
  "skill_id": "SKILL_ID_EXISTENTE",
  "user_id": "USER_ID"
}
```

### 3. Responder Preguntas
```bash
# PUT /api/v1/assessments/answer
{
  "session_id": "SESSION_ID",
  "question_number": 1,
  "answer": "opcion_correcta"
}
```

### 4. Generar Feedback
```bash
# POST /api/v1/assessments/evaluate
{
  "session_id": "SESSION_ID"
}
```

## Validación de Fix

### ✅ Problemas Resueltos
1. **Error de _id numérico**: MongoDB ahora usa ObjectId automáticamente
2. **Campo question_number faltante**: Todos los documentos tendrán este campo
3. **Validación Pydantic**: Los datos coinciden con el esquema definido

### ✅ Flujo Completo Funcional
1. Creación de evaluación genera preguntas con question_number secuencial
2. Respuestas se guardan correctamente por question_number
3. Evaluación procesa datos sin errores de validación
4. Feedback se genera exitosamente

## Comandos de Recuperación

Si surgen problemas similares en el futuro:

```bash
# 1. Limpiar base de datos
python scripts/clean_database.py
# Confirmar con: LIMPIAR

# 2. Verificar limpieza
python scripts/check_questions_structure.py

# 3. Reiniciar servicio
# El servicio creará automáticamente nuevas preguntas correctas
```

## Notas Importantes

- **Datos Preservados**: Las skills existentes no se eliminaron
- **Funcionalidad Intacta**: Todos los endpoints mantienen su comportamiento
- **Compatibilidad**: El nuevo formato es compatible con todas las operaciones
- **Performance**: Los índices compuestos mejoran la velocidad de consulta

## Estado Final

✅ Base de datos limpia
✅ Modelos Pydantic corregidos  
✅ Flujo completo funcional
✅ Scripts de mantenimiento disponibles
