
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

El uso de Conventional Commits (chore:, feat:, fix:) demuestra madurez en ingeniería de software, facilitando la auditoría de cambios y la integración continua (CI/CD).
chore: Tareas de soporte/estructura.
feat: Funcionalidad de negocio nueva.
fix: Corrección de un error o bug.

*Config.json*
¿Qué es esto y es JavaScript?
No es programación, es un formato de texto universal llamado JSON (JavaScript Object Notation). Nació de JavaScript, pero hoy lo leen todos los lenguajes del mundo (Python, SQL, R). Piensa en un JSON como un formulario digital de parejas: "Etiqueta": Valor.
Desglose línea por línea:
"seed": 42 (Semilla aleatoria):
Las computadoras no inventan números al azar reales; usan fórmulas matemáticas.
La semilla es el número inicial de esa fórmula. Si tú y el evaluador usan la semilla 42, a ambos les saldrán exactamente los mismos nombres, cédulas y montos "aleatorios". Esto se llama reproducibilidad.
"date_range" (Rango de fechas):
Cubre 12 meses históricos continuos (requisito estricto de la página 18 del PDF).
"null_rate": 0.05 (5% de valores nulos):
En la vida real, las bases de datos no son perfectas; a veces el cliente no llena el teléfono o la ciudad. Simulamos un 5% de datos vacíos para probar la calidad del pipeline.
"volumes" (Volumen por tabla):
Son exactamente los mínimos exigidos por la prueba (página 4 y 5): desde 50 productos hasta 500.000 transacciones.
"output_formats":
La prueba exige generar salidas en múltiples formatos heterogéneos (CSV, Parquet, JSON).
¿Cómo buscarlo en YouTube para profundizar?
"Qué es JSON y para qué sirve en 5 minutos"
"Qué es una semilla aleatoria (random seed) en programación"

*Generate_data.py* Simular el banco Finbank
Dos librerías estándar en Python:
pandas: Maneja tablas en memoria (como hojas de cálculo ultrarrápidas).
faker: Inventa nombres, fechas y documentos realistas.

TB_CLIENTES_CORE (La lista de clientes del banco) *Parecido al maestro de clientes que teniamos en 3M o en Sibelco y que solo podia crear cartera o el area comercial pero despues de haber pasado por un proceso de perfilación por el area comercial y su respectivo estudio de crédito*
TB_MOV_FINANCIEROS (Las transacciones con el campo id_cli). Las operaciones como siempre que no necesariamente tienen el detalle de los datos del cliente como dirección, telefono o a veces ni siquiera la sucursal pero si tienen el codigo del cliente y esta es la llave.

Que hice cuando instale las aplicaciones?

Qué pasó por debajo?
La tienda de aplicaciones (PyPI): pip se conectó por internet a PyPI (Python Package Index), el repositorio central mundial de código abierto de Python.
Descarga de paquetes (.whl): Descargó los archivos empaquetados (wheels, archivos comprimidos optimizados para tu procesador) y los instaló en tu disco duro.
Dependencias transitivas (el efecto dominó): Solo pediste 3 cosas (pandas, faker, pyarrow), pero pandas necesita matemáticos por debajo para funcionar (numpy, tzdata, etc.). pip calculó el árbol de dependencias e instaló todo lo necesario automáticamente.
El aviso amarillo (WARNING): Solo dice que no puedes ejecutar faker.exe directamente como un comando en PowerShell, pero dentro de nuestros scripts de Python funcionará al 100%

Mi prompt despues del archivo
te amo como siempre pero ese nivel de ingenieria yo creo que lo tiene un ingeniero muy avanzado entonces no se si estas siguiendo mi recomendación de hacerlo muy facil para poder yo sustentarlo y entenderlo y estudiarlo porque veo 170 lineas de codigo muy complejas (para alguien que sabe muy poco o nada de programación) y no se si valga la pena estudiar todos esos terminos y formulas y la estructura del archivo cuando posiblemente un evaluador lo descarte de una porque va a ver que no lo pudo hacer un principiante o porque este nivel de ingenieria no seria practico para mi en el corto tiempo puesto que es inalcanzable. Defiende tu archivo y explicame como podria un evaluador no creer (porque voy a hacer lo posible para transmitir que aunque no soy programador y lo hice con IA entiendo al menos lo que se hizo) que lo hizo un principiante pero si que es una solución practica o algo que en el corto tiempo yo podria comenzar a manejar sin generar errores graves en la operación o cosas que puedan fallar en la vida real

Sustentación Gemini

Te voy a ser 100% transparente: este script NO es de un ingeniero avanzado; es la forma más básica y directa que existe en Python.
1. ¿Por qué se ve largo e intimidante?
No es complejo, es repetitivo. El banco FinBank exige 6 tablas distintas con más de 40 columnas en total.
Un ingeniero avanzado habría creado clases abstractas, programación orientada a objetos o clústeres distribuidos en Spark.
Nosotros hicimos lo más básico del mundo: un simple ciclo (un "bucle") que repite filas y las guarda en una tabla de Pandas. Es largo solo porque son 6 tablas, no porque tenga matemáticas complejas.


El concepto de Seed Y las formulas mas importantes (randoms)

Aquí tienes la explicación conceptual y técnica para tus notas:
1. La Semilla (SEED): El "Modo Espejo"
En las líneas 14 a 19 del código ves esto:
code
Python
SEED = config["seed"] # Lee el número 42 de tu config.json
random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)
¿Qué es?: Las computadoras son incapaces de generar azar real; usan listas matemáticas infinitas precalculadas.
La analogía: Imagina una baraja de cartas revuelta. Si no pones semilla, cada vez que corres el script sacas cartas al azar. Si fijas la semilla en 42, le ordenas a Python barajar las cartas exactamente en el mismo orden siempre.
Tu defensa: "Fijar la semilla garantiza reproducibilidad. Si el auditor ejecuta mi código hoy y en un año, obtendrá el mismo centavo y el mismo cliente."
2. Las 3 fórmulas clave del código:
random.choice(["App", "Web", "Cajero"]) (La Ruleta):
Elige un elemento al azar dentro de una lista de opciones. Así simulamos por qué canal compró el cliente.
np.random.normal(loc=650, scale=80) (La Campana de Gauss):
loc=650 es la media (el promedio).
scale=80 es la desviación estándar (la dispersión).
Genera el puntaje de Datacrédito realista: la masa está entre 570 y 730, y casi nadie tiene menos de 300 o más de 850.
df.to_parquet(...) (El estándar Big Data):
Un CSV es texto plano (pesado y lento).
Parquet guarda los datos comprimidos por columnas en ceros y unos. Pesa 80% menos y la nube de Azure lo procesa 10 veces más rápido.

Se generaron los archivos después de entender un poco la forma en que se escribió el codigo y se corrigieron dos lineas de codigo: "# Formato CSV con firma UTF-8 para Excel
df_sucursales.to_csv(os.path.join(out_dir, "TB_SUCURSALES_RED.csv"), index=False, encoding="utf-8-sig")
df_clientes.to_csv(os.path.join(out_dir, "TB_CLIENTES_CORE.csv"), index=False, encoding="utf-8-sig")" Puesto que no estaban saliendo los nombres y demas datos de las tablas con las tildes "encoding="utf-8-sig"".

¿Por qué le llamaron Mermaid?
Su creador (Knut Sveidqvist) lo llamó Mermaid ("Sirena") porque quería una herramienta ágil y fluida que pudiera "nadar" dentro del texto Markdown sin complicaciones. Hoy es el estándar adoptado por GitHub, Microsoft y GitLab para hacer diagramas técnicos sin tocar programas de diseño.

Recordando relacionamiento de tablas y tipos de variables

1. Relación 1 a 1 (Uno a Uno)
Cada fila de la Tabla A se conecta con una única fila exclusiva en la Tabla B.
Se utiliza principalmente para aislar datos confidenciales (como salarios o historiales médicos) del resto del sistema.
Optimiza la velocidad al separar información pesada (como fotos o contratos) de los datos de consulta rápida.
Ambas tablas comparten exactamente la misma llave única de identificación.
2. Relación 1 a N (Uno a Muchos)
Un único registro maestro se vincula con múltiples registros dependientes en otra tabla.
Es el patrón más común en el mundo de los negocios para registrar actividades históricas (compras, visitas, pagos).
La llave del maestro viaja a la tabla de detalle como llave foránea (Foreign Key) para no repetir datos innecesarios.
Garantiza que si el cliente cambia de dirección, solo se actualiza una sola vez en el maestro.
3. Relación N a N (Muchos a Muchos)
Múltiples registros de la Tabla A se conectan con múltiples registros de la Tabla B.
No se puede conectar de forma directa en bases de datos relacionales; requiere obligatoriamente una tabla intermedia o "puente".
Ejemplo clásico: Estudiantes y Cursos (un alumno toma varios cursos y un curso tiene muchos alumnos).


Este diagrama es el plano arquitectónico del banco. Aquí le dices al sistema cómo se debe comportar cada dato:
int (Integer): Números enteros sin decimales (como id_cli: 1, 2, 3 o score_buro: 650).
string: Cadenas de texto o letras (como nomb_cli: Carlos o ciudad: Bogotá).
date / time: Fechas (2026-05-10) y horas (14:30:00).
decimal: Números con centavos para plata y finanzas (vr_mov: 54200.50). En bancos nunca se usa texto para el dinero para poder sumar y calcular intereses.
Y lo más importante que ves al lado:
PK (Primary Key / Llave Primaria): El identificador único que no se puede repetir (la cédula de la fila).
FK (Foreign Key / Llave Foránea): La columna que viaja a otra tabla para hacer la conexión (el VLOOKUP).

Preguntas de la generación de los archivos schema y load_to_sql

*1. ¿Por qué num_doc es TEXT y no INTEGER?*
Existe una regla de oro en Ingeniería de Datos:
"Si con ese número jamás vas a hacer operaciones matemáticas (sumar, restar, sacar promedios), guárdalo siempre como TEXTO".
Pérdida de ceros a la izquierda: Si una persona tiene documento 00123456, al guardarlo como número la base de datos lo convierte en 123456 y corrompe la cédula.
Cédulas de Extranjería / Pasaportes: Muchos documentos de identidad contienen letras (ej. E-104928). Si fuera entero, el sistema fallaría al intentar guardarlo.

*2. ¿Por qué fec_nac es TEXT en el schema.sql?*
En bases de datos gigantes como Oracle o SQL Server existe el tipo DATE. Sin embargo, el motor liviano SQLite maneja todas las fechas bajo el estándar internacional ISO-8601 en formato TEXTO (YYYY-MM-DD). Esto permite ordenar fechas alfabéticamente de menor a mayor sin errores de cálculo.

*3. Llaves Foráneas y NOT NULL (Le atinaste perfecto)*
NOT NULL: Significa "campo obligatorio". Si el sistema intenta guardar una sucursal sin nombre, la base de datos bloquea el registro por falta de calidad.
FOREIGN KEY (...) REFERENCES ...: Es el candado de integridad. Le dice a la base de datos: "Si alguien intenta registrar una transacción con un id_cli = 999999 y ese cliente no existe en TB_CLIENTES_CORE, no permitas guardar la transacción".

*4. ¿Qué son os y sqlite3 en Python?*
import os (Operating System / Explorador de archivos):
Es la librería nativa de Python para interactuar con tu disco duro.
Permite que el código funcione igual en tu computador, en el mío o en un servidor de Linux sin que se dañen las rutas de las carpetas (os.path.join).
import sqlite3 (El motor de base de datos):
Es un motor relacional SQL completo que viene incluido gratis dentro de Python. No requiere servidores ni instalaciones complejas; crea un archivo (finbank_source.db) que se comporta exactamente igual a un SQL Server o PostgreSQL.
conn (Connection) y cursor:
conn: Es como levantar el teléfono y abrir la línea de comunicación con la base de datos.
cursor: Es el mensajero. Le entregas una orden en SQL (cursor.execute("SELECT COUNT(*)...")) y él te trae la respuesta a la pantalla (cursor.fetchone()).
df.to_sql(...):
Es el camión de mudanza: toma la tabla que tienes en memoria con Pandas y la inserta con todas sus filas directamente en la tabla SQL relacional.

TF
Terraform
Este archivo contiene planos de infraestructura en lenguaje HCL 

1. ¿Por qué 4 archivos y no uno solo gigante?
Terraform es tan inteligente que al ejecutarse une todos los archivos .tf en uno solo mentalmente.
Podríamos meter todo en un solo archivo de 600 líneas, pero separarlo en 4 es el estándar de oro de la industria:
Archivo	Rol en la obra	¿Para qué sirve?
providers.tf	Los Contratistas	Define con qué empresas trabajamos (Azure y generador de nombres únicos).
variables.tf	La Botonera	Los valores que puedes cambiar (región, ambiente dev o prod) sin tocar los planos.
main.tf	Los Planos de Construcción	La lista exacta de edificios a construir (Data Lake, Bóveda, Fábrica).
outputs.tf	La Factura de Entrega	Le avisa al equipo: "aquí quedó construida la bodega y esta es su dirección web".
2. ¿Cómo funcionan las variables en la práctica?
Imagina que en main.tf tienes que escribir el país o región 15 veces.
Sin variables (Mala práctica): Escribes "eastus2" quemado en 15 lugares distintos. Si el banco decide mudarse a Europa, tienes que buscar y cambiar 15 líneas arriesgándote a olvidar una.
Con variables (Buena práctica): En los planos escribes var.location. Si el banco cambia de sede, cambias una sola línea en variables.tf y los 15 edificios se mudan solos.

Fundamentos de Ingeniería de Datos: Resumen Académico del Proyecto

I. El Cambio de Paradigma: Desarrollo de Apps vs. Ingeniería de Datos
En el desarrollo tradicional de software (como tu app de asambleas con Node.js y npm run dev):
El objetivo es la interacción del usuario en tiempo real (pantallas, botones, formularios y APIs transaccionales).

En la Ingeniería de Datos:
El objetivo es la trazabilidad, pureza y procesamiento masivo del dato histórico. No construimos interfaces visuales; construimos tuberías analíticas automatizadas (Pipelines) que transportan millones de registros desde sistemas operativos hacia almacenes optimizados para la toma de decisiones empresariales.

II. Fase 1: Simulación de Sistemas Transaccionales (OLTP) y Modelado Relacional

Sistemas Transaccionales (OLTP):
Son bases de datos diseñadas para el día a día operativo (registrar un pago, crear un cliente).
Se estructuran bajo Reglas de Normalización para no duplicar información innecesariamente.

Integridad Referencial y Jerarquía de Entidades:
Entidades Fuertes (Maestras / Dimensiones): Clientes, Productos, Sucursales. Tienen existencia propia e identificadores únicos (Primary Keys / PK).

Entidades Débiles (Eventos / Transacciones): Movimientos bancarios, Comisiones, Obligaciones. Dependen obligatoriamente de una entidad fuerte mediante llaves foráneas (Foreign Keys / FK).

Principio de Ingesta: No puede existir una transacción de un cliente que no ha sido creado previamente.
Determinismo y Reproducibilidad (Random Seed):
En ciencia de la computación, el azar no existe; se utilizan generadores de números pseudoaleatorios.
La Semilla (Seed = 42) fija el punto de partida del algoritmo. Esto asegura que ante cualquier auditoría o evaluación técnica, el código genere exactamente los mismos registros, importes y fechas, eliminando la variabilidad no controlada.

Inyección Controlada de Ruido y Calidad:
La data real de las empresas nunca es perfecta. Para probar la robustez del pipeline, se introdujo intencionalmente:
Una tasa controlada de datos ausentes (5% de valores nulos).
Anomalías documentadas: Registros duplicados exactos y fechas fuera del rango operacional.


III. Fase 2: Infraestructura como Código (IaC) y Arquitectura Cloud en Azure

El Concepto de Declaratividad en Terraform:
A diferencia de los scripts imperativos (donde le dices al computador "haz A, luego haz B, luego haz C"), Terraform es declarativo: describes en archivos .tf el estado final deseado de la arquitectura, y el motor de Terraform calcula internamente las llamadas API necesarias para construirlo en Azure sin intervención humana.
Componentes Arquitectónicos Desplegados en Azure:
Resource Group (rg-finbank-dev): Frontera lógica de aislamiento para gobernanza administrativa, seguridad y control del ciclo de vida de los activos.

Azure Data Lake Storage Gen2 (stfinbankdevrch7): Sistema de almacenamiento de objetos optimizado para analítica masiva mediante Espacio de Nombres Jerárquico (Hierarchical Namespace - HNS). Esto permite operaciones atómicas sobre directorios (moverse entre carpetas en milisegundos en vez de reescribir archivos).

Azure Data Factory (adf-finbank-dev-rch7): Servicio de orquestación ETL/ELT para programar y monitorear la ejecución de los flujos de datos.

Azure Key Vault (kv-finbank-rch7): Almacén centralizado de secretos bajo estándares criptográficos. Elimina la práctica riesgosa de quemar credenciales en el código fuente (Secrets Sprawl).
Log Analytics Workspace (law-finbank-dev): Repositorio central de telemetría y auditoría operacional para responder "quién, cuándo y qué se ejecutó".

Action Group (ag-finbank-alerts): Sistema de suscripción y notificación reactiva que dispara alertas automáticas por correo ante eventos de falla.

Gobernanza Financiera (FinOps):
Se aplicó la política de menor costo operacional (Replicación LRS local, retención de logs a 30 días y nivel de servicio Standard), respaldado por un presupuesto preventivo con alertas al 80% del gasto devengado.

## IV. Fase 3: Arquitectura Medallón (Procesamiento Progresivo del Dato)

### 1. Capa Bronze (Raw / Crudo)
* **Propósito:** Ingesta fiel desde el origen sin alterar datos.
* **Metadatos de Auditoría:**
  * `fecha_ingesta`: Momento exacto de captura.
  * `sistema_fuente`: Origen del dato (`FINBANK_CORE_SQL`).
  * `id_lote` (UUID): Identificador único de ejecución para trazabilidad.
* **Particionamiento Temporal:** Organización física en subcarpetas (`year/month/day`) para evitar escaneos completos del disco en consultas incrementales.

### 2. Capa Silver (Enriquecimiento, Calidad y Seguridad)
* **Gobierno de Privacidad (Habeas Data):** Encriptación con función criptográfica unidireccional `SHA-256` sobre campos sensibles (`num_doc`). El dato original desaparece; se conserva un token irreconocible pero único para poder hacer cruces.
* **Aislamiento en Cuarentena (`TB_ERRORES_PIPELINE`):** Los registros con fechas absurdas (2030) o valores negativos no se eliminan silenciosamente; se envían a una tabla de auditoría con la causa documentada.
* **Regla Analítica de Fraude:** Marcado estadístico de anomalías cuando el monto supera `Media + 3 Desviaciones Estándar` (`ind_sospechoso = 1`).

### 3. Capa Gold (Modelo Dimensional y Lógica de Negocio)
* **Modelo en Estrella:** Separación de Dimensiones (`dim_clientes`, `dim_productos`, `dim_geografia`, `dim_canal`) y Hechos (`fact_transacciones`, `fact_cartera`).
* **Regulación Financiera:** Cálculo de tramos de mora (*Buckets*: Al día, Rango 1, Rango 2, Rango 3, Deteriorado) y cálculo de provisión bancaria porcentual según riesgo.
* **Agregaciones Ejecutivas:** Tabla `kpi_diarios_cartera` para que la junta directiva consulte saldos totales, cartera vencida y tasa de mora por ciudad y producto en tiempo real.

### 4. Pruebas Automatizadas de Calidad (Data Quality)
* Conjunto de 5 aserciones automatizadas (Completitud, No Nulidad, Rango Válido, Integridad Referencial y Unicidad) con resultado 5/5 APROBADO (100%).


### 1. ¿Qué es RBAC? (La analogía del edificio de oficinas)
RBAC significa Role-Based Access Control (Control de Acceso Basado en Roles).
Piensa en los carnets de acceso de un banco:
El Carnet de Administrador (Owner): Abre la bóveda, el tejado, los servidores y las oficinas.
El Carnet de Ingeniero de Datos (Storage Blob Data Contributor): Puede entrar a las tres bodegas (bronze, silver, gold) a meter y sacar datos, pero no puede cambiar la tarjeta de crédito con la que se paga Azure.
El Carnet de Analista (Storage Blob Data Reader): El torniquete solo le abre la puerta del piso Gold. Si intenta pasar su carnet en Bronze o Silver, la puerta suena en rojo y dice: Acceso Denegado (HTTP 403 Forbidden).