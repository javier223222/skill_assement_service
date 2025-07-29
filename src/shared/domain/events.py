"""
Sistema de eventos de dominio
Implementa el patrón Domain Events para DDD
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Callable, Any
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from shared.domain.base_entity import DomainEvent


class EventPriority(Enum):
    """Prioridades para el procesamiento de eventos"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class EventHandler:
    """Wrapper para handlers de eventos con metadatos"""
    handler: Callable[[DomainEvent], Any]
    priority: EventPriority
    async_handler: bool = True


class IDomainEventHandler(ABC):
    """Interfaz para handlers de eventos de dominio"""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Maneja un evento de dominio específico"""
        pass


class EventDispatcher:
    """
    Dispatcher central para eventos de dominio
    Implementa patrón Observer para desacoplamiento
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[DomainEvent], Any],
        priority: EventPriority = EventPriority.NORMAL,
        async_handler: bool = True
    ) -> None:
        """
        Suscribe un handler a un tipo de evento específico
        
        Args:
            event_type: Tipo de evento (ej: "SkillCreated")
            handler: Función o método que manejará el evento
            priority: Prioridad del handler
            async_handler: Si el handler es asíncrono
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        event_handler = EventHandler(handler, priority, async_handler)
        self._handlers[event_type].append(event_handler)
        
        # Ordena por prioridad (mayor prioridad primero)
        self._handlers[event_type].sort(
            key=lambda h: h.priority.value, 
            reverse=True
        )
        
        self._logger.info(f"Handler registered for event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Desuscribe un handler de un tipo de evento"""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] 
                if h.handler != handler
            ]
            self._logger.info(f"Handler unregistered for event type: {event_type}")
    
    async def dispatch(self, event: DomainEvent) -> None:
        """
        Despacha un evento a todos sus handlers suscritos
        
        Args:
            event: Evento de dominio a procesar
        """
        event_type = event.event_type
        
        if event_type not in self._handlers:
            self._logger.debug(f"No handlers for event type: {event_type}")
            return
        
        handlers = self._handlers[event_type]
        self._logger.info(f"Dispatching event {event_type} to {len(handlers)} handlers")
        
        # Ejecuta handlers síncronos primero
        sync_handlers = [h for h in handlers if not h.async_handler]
        for handler_wrapper in sync_handlers:
            try:
                handler_wrapper.handler(event)
                self._logger.debug(f"Sync handler executed for {event_type}")
            except Exception as e:
                self._logger.error(f"Error in sync handler for {event_type}: {e}")
        
        # Ejecuta handlers asíncronos en paralelo
        async_handlers = [h for h in handlers if h.async_handler]
        if async_handlers:
            tasks = []
            for handler_wrapper in async_handlers:
                task = asyncio.create_task(
                    self._execute_async_handler(handler_wrapper.handler, event)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_async_handler(self, handler: Callable, event: DomainEvent) -> None:
        """Ejecuta un handler asíncrono con manejo de errores"""
        try:
            await handler(event)
            self._logger.debug(f"Async handler executed for {event.event_type}")
        except Exception as e:
            self._logger.error(f"Error in async handler for {event.event_type}: {e}")
    
    async def dispatch_many(self, events: List[DomainEvent]) -> None:
        """Despacha múltiples eventos"""
        for event in events:
            await self.dispatch(event)
    
    def get_handler_count(self, event_type: str) -> int:
        """Obtiene el número de handlers para un tipo de evento"""
        return len(self._handlers.get(event_type, []))
    
    def get_registered_event_types(self) -> List[str]:
        """Obtiene todos los tipos de eventos registrados"""
        return list(self._handlers.keys())


# Instancia global del dispatcher
event_dispatcher = EventDispatcher()


class DomainEventPublisher:
    """
    Publisher que recolecta y publica eventos de aggregates
    """
    
    def __init__(self, dispatcher: EventDispatcher = None):
        self._dispatcher = dispatcher or event_dispatcher
    
    async def publish_events_from_aggregate(self, aggregate) -> None:
        """
        Publica todos los eventos de un aggregate y los limpia
        
        Args:
            aggregate: Aggregate root que contiene eventos
        """
        events = aggregate.publish_domain_events()
        await self._dispatcher.dispatch_many(events)
    
    async def publish_event(self, event: DomainEvent) -> None:
        """Publica un evento individual"""
        await self._dispatcher.dispatch(event)


# Instancia global del publisher
domain_event_publisher = DomainEventPublisher()


def domain_event_handler(event_type: str, priority: EventPriority = EventPriority.NORMAL):
    """
    Decorador para registrar handlers de eventos de dominio
    
    Usage:
        @domain_event_handler("SkillCreated")
        async def handle_skill_created(event: DomainEvent):
            # Lógica del handler
            pass
    """
    def decorator(handler_func):
        event_dispatcher.subscribe(event_type, handler_func, priority)
        return handler_func
    return decorator
