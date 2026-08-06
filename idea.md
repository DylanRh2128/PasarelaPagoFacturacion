Quiero construir un proyecto backend para mi portafolio de GitHub: una API 
que integra una pasarela de pagos (Stripe) y genera facturas en PDF 
automáticamente tras un pago exitoso.

Stack propuesto: Python + FastAPI + PostgreSQL (para registrar transacciones 
y clientes) + Stripe + una librería para generación de PDF. Soy desarrollador 
junior y busco tanto un proyecto de portafolio convincente como aprendizaje 
real de integraciones de pago.

Ayúdame a:
1. Definir el alcance mínimo viable (ej. pago único por un producto/servicio 
   simulado, sin necesidad de suscripciones todavía)
2. Diseñar los endpoints y el flujo completo: crear intento de pago, recibir 
   confirmación vía webhook, generar y guardar la factura
3. Explicar cómo manejar webhooks de Stripe de forma segura (verificación 
   de firma, idempotencia)
4. Señalar los riesgos de seguridad a los que debo prestar atención (ej. 
   nunca exponer llaves secretas, validar montos en el servidor, no confiar 
   solo en el frontend)
5. Listar los pasos de implementación en orden, del más simple al más avanzado
No escribas código todavía, solo el plan.