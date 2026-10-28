
**Day 1**
1. Gobernanza de Costos y Nube (FinOps)
Decisión: Despliegue en un entorno sandbox dedicado en Microsoft Azure.
Sustentación: Se aplicó una política de FinOps preventiva desde el minuto cero mediante un presupuesto de seguridad ($5 USD) con alerta temprana al 80% del gasto real devengado.
Impacto: Demuestra control presupuestal, mitigación de riesgos de sobrecosto y monitoreo activo de recursos antes de desplegar cómputo.
2. Selección Estratégica de Negocio (Escenario A - FinBank)
Decisión: Sector Banca y Servicios Financieros.
Sustentación:
Eficiencia de Cómputo: Con un volumen de ~620.000 registros, permite validar arquitecturas Big Data sin saturar el entorno local ni agotar los créditos en la nube.
Valor Analítico: Modela tres casos de uso críticos de la industria financiera: cálculo de mora por tramos (buckets), detección de transacciones atípicas (prevención de fraude) y rentabilidad a largo plazo (Customer Lifetime Value - CLTV).
3. Estándar de Repositorio y Arquitectura Limpia
Decisión: Repositorio en GitHub estructurado según las pautas corporativas del reto (/infra, /data-generation, /pipelines, /orchestration, /docs).
Sustentación: Garantiza la separación de responsabilidades (Separation of Concerns), trazabilidad de cambios (CHANGELOG.md) y preparación para la exclusión rigurosa de secretos y estados de infraestructura (.gitignore).

**Explicación del proceso de creación de carpetas**
1. .gitignore (El escudo de seguridad)
¿Qué es?: Una lista negra que le dice a Git: "estos archivos jamás los subas a internet".
Por qué existe: Si subes por error un archivo con contraseñas, claves de Azure o el archivo terraform.tfstate (que guarda tu infraestructura en texto plano), cualquier persona puede vulnerar tu nube o generar cobros millonarios.
2. Relación lógica de las carpetas (Flujo de vida del dato)
Imagina construir una fábrica automatizada:
/infra (Los cimientos): Contiene el código de Terraform. Antes de mover un solo dato, necesitas encender los discos duros, bases de datos y bóvedas en Azure. Es la infraestructura física expresada en código (IaC).
/data-generation (La materia prima): Simula el sistema del banco. Genera los archivos fuente con clientes, compras y mora para simular la operación del mundo real.
/pipelines (La línea de ensamblaje): Aplica la arquitectura Medallón:
Bronze: Ingesta cruda (tal cual llega).
Silver: Limpieza, eliminación de nulos y enmascaramiento de datos personales (GDPR/Habeas Data).
Gold: Métricas de negocio (KPIs, tablas estrella).
/orchestration (El director de turno): El robot que ejecuta todo a las 02:00 AM. Controla dependencias: no permite procesar Silver si Bronze falló.
/docs (Los manuales de ingeniería): Diagramas de arquitectura y catálogo de datos para que auditores y analistas entiendan el modelo.
**Tema clave para investigar: "Separation of Concerns (SoC) en Data Engineering".**

**Gitinore** (es el archivo que le dice a Git esto no va para Internet porque son las claves de mi app)
Sustentación: La inclusión temprana de un .gitignore estricto previene la fuga involuntaria de secretos (Secrets Sprawl) y garantiza que los estados de infraestructura (state files) solo se almacenen en backends remotos y seguros.
