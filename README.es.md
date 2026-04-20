# Subscription Analytics Lab - Analisis de Revenue, Retencion y Churn

Proyecto avanzado de portafolio para demostrar analisis de datos aplicado a un negocio de suscripcion, con capa SQL reutilizable y dashboard para monitoreo de revenue y salud del cliente.

## Problema que resuelve

Un negocio de suscripcion necesita mas que una grafica simple de ingresos. En la practica, un analista suele combinar:

1. contexto del ciclo de vida del cliente,
2. comportamiento de cobro y facturacion,
3. patrones de uso del producto,
4. senales de soporte,
5. retencion por cohortes,
6. reporting que permita tomar decisiones con rapidez.

Este proyecto simula ese flujo de trabajo de punta a punta.

## Habilidades que demuestra

- Python para procesamiento y analitica
- SQL con SQLite para reporting
- modelado analitico a nivel cliente-mes
- analisis de cohortes
- scoring de riesgo de churn usando senales operativas y de comportamiento
- diseno de KPIs para MRR, ARPA, churn y net revenue retention
- visualizacion con Streamlit

## Modelo de Datos

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

## Arquitectura

1. Generacion de datos: [src/generate_sample_data.py](src/generate_sample_data.py)
2. Construccion analitica: [src/build_analytics.py](src/build_analytics.py)
3. Orquestacion del pipeline: [src/run_pipeline.py](src/run_pipeline.py)
4. Dashboard: [src/dashboard.py](src/dashboard.py)
5. Vistas SQL: [sql/schema.sql](sql/schema.sql)
6. Consultas del portafolio: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)

## Funcionalidades Analiticas

### 1. Capa mensual de KPIs

El proyecto exporta metricas recurrentes como:

- clientes activos
- MRR
- revenue cobrado
- ARPA
- churn rate
- net revenue retention
- CSAT promedio
- adopcion promedio de funcionalidades

### 2. Retencion por cohortes

Cada cliente queda asociado a una cohorte de alta y se sigue por `months_since_signup`, lo que permite analizar retencion a lo largo del tiempo.

### 3. Scoring de riesgo de churn

Cada registro cliente-mes incluye un score de riesgo derivado de:

- uso del producto frente a actividad reciente
- fallos de pago
- tickets de alta prioridad
- CSAT bajo
- contraccion de revenue recurrente

### 4. Monitoreo de calidad del revenue

La capa analitica marca periodos inusuales considerando crecimiento de MRR, churn y comportamiento de NRR.

## Ultimo Snapshot

Las salidas actuales muestran:

- `232` clientes activos en el mes mas reciente
- `61,418` de MRR
- `264.73` de ARPA
- `1.28%` de logo churn
- `4.33` de CSAT promedio
- `LATAM` como region mas fuerte por MRR
- `Scale` como plan lider por MRR total

## Por que este proyecto es fuerte para portafolio

Este repositorio funciona bien para revision tecnica porque demuestra mas que exploracion aislada en notebooks.

Incluye:

- generacion reproducible de datos
- modelo analitico estructurado
- consultas SQL reutilizables
- salidas exportadas en CSV y Markdown
- un pipeline que materializa la base SQLite de forma local
- dashboard que muestra revenue y salud del cliente

Eso lo vuelve un proyecto fuerte para roles de `data analysis`, `business analytics`, `SQL`, `reporting` y bases de `analytics engineering`.

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

## Ejecutar pipeline

```bash
python src/run_pipeline.py
```

## Ejecutar dashboard

```bash
python -m streamlit run src/dashboard.py
```

## Ejecutar pruebas

```bash
python -m unittest discover -s tests
```

## Salidas del proyecto

La version publica del portafolio mantiene el repositorio liviano. Al ejecutar el pipeline se regeneran de forma local los archivos fuente en `data/`, la capa analitica cliente-mes y la base SQLite.

- Serie de KPIs: [output/monthly_kpis.csv](output/monthly_kpis.csv)
- Retencion por cohortes: [output/cohort_retention.csv](output/cohort_retention.csv)
- Resumen por segmentos: [output/segment_summary.csv](output/segment_summary.csv)
- Watchlist de churn: [output/churn_risk_watchlist.csv](output/churn_risk_watchlist.csv)
- Anomalias de revenue: [output/revenue_anomalies.csv](output/revenue_anomalies.csv)
- Reporte: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)

## Capa SQL

El repositorio incluye activos SQL reutilizables:

- esquema y vistas: [sql/schema.sql](sql/schema.sql)
- consultas del portafolio: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)

La capa SQL esta pensada para soportar:

- revision de KPIs recientes
- analisis de retencion
- listas de riesgo
- mezcla de planes
- salud regional del negocio

## Temas de Discusion Tecnica

1. Como el grano cliente-mes soporta analitica y reporting
2. Por que la retencion por cohortes importa en un negocio de suscripcion
3. Que senales son utiles para estimar riesgo de churn
4. Como cambia la interpretacion cuando se evalua calidad del revenue y no solo crecimiento bruto
5. Como escalar este proyecto hacia un warehouse o flujo BI mas grande
