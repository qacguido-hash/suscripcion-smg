# Cerebro Caución – San Patricio Seguros

Base de conocimiento del área de Caución. Tiene dos objetivos:

1. **Aprender a pensar como suscriptor de la casa**: registrar criterios, decisiones y razonamientos (sobre todo lo que transmite la jefatura) para poder consultarlos después.
2. **Dejar el área documentada**: que una persona nueva pueda entender los procesos (emisión, cobranzas, endosos, siniestros) y los sistemas sin depender de nadie.

> Regla de oro: acá **no** se copia material confidencial de otras compañías. Se usan conceptos y estructura; el contenido es propio de San Patricio.

---

## Estructura

| Carpeta / archivo | Qué va | Cuándo se actualiza |
|---|---|---|
| `bitacora.md` | Notas crudas del día: lo que dijo el jefe, dudas, aprendizajes. Sin ordenar. | Todos los días, rápido. |
| `casos/` | Un archivo por negocio analizado, con la plantilla `_plantilla.md`. | Cada vez que se decide un negocio relevante (emitido, rechazado o con condiciones). |
| `criterios/` | Lineamientos de suscripción ya "destilados": cómo se analiza un tomador, qué se pide por ramo, contragarantías, límites. | Cuando un patrón de la bitácora o de los casos se repite y se convierte en regla. |
| `procesos/` | Manuales paso a paso de cada tarea y del sistema. | Cuando se aprende o cambia un proceso. |
| `normativa/` | Resúmenes de normativa SSN, condiciones generales, pliegos tipo. | Cuando sale algo nuevo o se consulta algo puntual. |
| `glosario.md` | Términos, siglas, jerga interna. | Cuando aparece un término nuevo. |

## El circuito

```
lo que pasa en el día  ──►  bitacora.md  ──►  (revisión semanal)  ──►  casos/  +  criterios/  +  procesos/
```

- La **bitácora** es la entrada: no importa la prolijidad, importa que quede escrito con fecha.
- Una vez por semana se revisa la bitácora con Claude y se ordena: cada nota pasa a un caso, a un criterio, a un proceso o se descarta. Lo procesado se marca con ✅.

## Convenciones

- **Nombres de casos**: `AAAA-MM-DD-actividad-ramo.md` → `2026-12-03-constructora-obra-publica.md`.
- **Datos sensibles**: los tomadores se identifican con un código o un nombre genérico (ej. "Constructora A"), no con CUIT ni datos personales, salvo que el repositorio sea estrictamente privado y se decida lo contrario.
- **Montos**: en pesos o dólares, indicando moneda y fecha (la inflación hace que un monto sin fecha no sirva para comparar).
- **Fuente**: cuando un criterio viene del jefe, se anota "según [jefe], fecha". Cuando es criterio de mercado general, se anota "criterio general".
- **Estado de los criterios**: `🟢 confirmado` (validado en la casa) · `🟡 a validar` (idea propia o de mercado, falta confirmar con jefatura).

## Cómo consultar a Claude

Ejemplos de consultas que este cerebro permite responder:

- "Tengo una constructora chica que pide ejecución de contrato por $X para una obra municipal. ¿Hay algún caso parecido? ¿Qué se decidió?"
- "¿Qué documentación pedimos para una garantía aduanera?"
- "Ordená la bitácora de esta semana."
- "Armá el manual de emisión con lo que te conté hoy."
