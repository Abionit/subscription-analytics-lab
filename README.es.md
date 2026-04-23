# Subscription Analytics Lab - Analisis de Revenue, Retencion y Churn

Proyecto de analitica de suscripciones que muestra como SQL, Python y reporting pueden usarse para monitorear revenue, retencion y salud del cliente.

## Pregunta De Negocio

Que senales ayudan a identificar temprano presion sobre la retencion, riesgo de revenue y deterioro en la salud del cliente?

Este proyecto responde esa pregunta combinando contexto del ciclo de vida del cliente, comportamiento de facturacion, uso del producto, actividad de soporte, KPIs y salidas analiticas faciles de revisar.

## Que Demuestra Este Repositorio

- Generacion de datos y pipeline analitico con Python
- Reporting con SQL y vistas reutilizables
- Modelado cliente-mes para analitica de suscripcion
- Diseno de KPIs para MRR, ARPA, logo churn y net revenue retention
- Analisis de retencion por cohortes
- Scoring de riesgo de churn con senales operativas y de comportamiento
- Comunicacion de resultados mediante Streamlit

## Snapshot Actual

Las salidas actuales muestran:

- `232` clientes activos en el mes mas reciente
- `61,418` de MRR
- `264.73` de ARPA
- `1.28%` de logo churn
- `4.33` de CSAT promedio
- `LATAM` como region mas fuerte por MRR
- `Scale` como plan lider por MRR total

## Modelo De Datos

El pipeline genera un dataset sintetico con cinco entidades principales:

1. `customers.csv`
2. `subscriptions.csv`
3. `billing_events.csv`
4. `daily_product_usage.csv`
5. `support_tickets.csv`

Estas fuentes se transforman en una capa analitica reutilizable:

- `customer_monthly_metrics.csv`
- `monthly_kpis.csv`
- `cohort_retention.csv`
- `segment_summary.csv`
- `churn_risk_watchlist.csv`
- `revenue_anomalies.csv`

## Flujo De Trabajo

1. Generar datos fuente: [src/generate_sample_data.py](src/generate_sample_data.py)
2. Construir salidas analiticas: [src/build_analytics.py](src/build_analytics.py)
3. Ejecutar el pipeline completo: [src/run_pipeline.py](src/run_pipeline.py)
4. Revisar el dashboard: [src/dashboard.py](src/dashboard.py)
5. Consultar la capa SQLite: [sql/schema.sql](sql/schema.sql) y [sql/portfolio_queries.sql](sql/portfolio_queries.sql)

## Cobertura Analitica

### Capa De KPIs

El proyecto calcula metricas de negocio como:

- clientes activos
- MRR
- revenue cobrado
- ARPA
- churn rate
- net revenue retention
- CSAT promedio
- adopcion promedio de funcionalidades

### Retencion Por Cohortes

Cada cliente queda asociado a una cohorte de alta y se sigue por `months_since_signup`, lo que permite revisar el comportamiento de retencion a lo largo del tiempo.

### Scoring De Riesgo De Churn

Cada registro cliente-mes incluye un score de riesgo derivado de:

- uso del producto frente a actividad reciente
- fallos de pago
- tickets de alta prioridad
- CSAT bajo
- contraccion de revenue recurrente

### Monitoreo De Calidad Del Revenue

La capa analitica marca periodos inusuales usando crecimiento de MRR, churn y comportamiento de NRR.

## Valor Para Revision

Este repositorio va mas alla de una exploracion aislada en notebooks. Muestra:

- un flujo reproducible
- metricas orientadas a negocio
- activos SQL reutilizables
- salidas exportadas en CSV y Markdown
- un pipeline que materializa SQLite de forma local
- un dashboard que resume senales accionables

Eso lo vuelve relevante para roles de `data analysis`, `business analytics`, `SQL`, `reporting` y bases de `analytics engineering`.

## Estructura Del Repositorio

- [src/](src): scripts del pipeline y dashboard
- [sql/](sql): esquema y consultas
- [output/](output): salidas analiticas representativas
- [tests/](tests): pruebas unitarias
- [CHANGELOG.md](CHANGELOG.md): notas de version

## Setup

```bash
python -m venv .venv
```

Activa el entorno virtual:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar El Pipeline

```bash
python src/run_pipeline.py
```

## Ejecutar El Dashboard

```bash
python -m streamlit run src/dashboard.py
```

## Ejecutar Las Pruebas

```bash
python -m unittest discover -s tests
```

## Salidas Del Proyecto

El repositorio mantiene livianos los datos generados. Al ejecutar el pipeline se regeneran de forma local los archivos fuente, la capa analitica cliente-mes y la base SQLite.

- Serie de KPIs: [output/monthly_kpis.csv](output/monthly_kpis.csv)
- Retencion por cohortes: [output/cohort_retention.csv](output/cohort_retention.csv)
- Resumen por segmentos: [output/segment_summary.csv](output/segment_summary.csv)
- Watchlist de churn: [output/churn_risk_watchlist.csv](output/churn_risk_watchlist.csv)
- Anomalias de revenue: [output/revenue_anomalies.csv](output/revenue_anomalies.csv)
- Reporte: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)

## Capa SQL

El repositorio incluye activos SQL reutilizables:

- esquema y vistas: [sql/schema.sql](sql/schema.sql)
- consultas analiticas: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)

La capa SQL soporta:

- revision de KPIs recientes
- analisis de retencion
- listas de riesgo
- mezcla de planes
- salud regional del negocio
