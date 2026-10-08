# Diagrama de Linaje y Trazabilidad de Datos (DAG)

**Generado**: 2026-10-01T20:02:21.282669 | **Run ID**: `RUN_20261001_200147`

```mermaid
flowchart LR
    classDef bronze fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef silver fill:#eeeeee,stroke:#333,stroke-width:1px;
    classDef gold fill:#d4edda,stroke:#28a745,stroke-width:2px;
    bronze_sipsa_abastecimientos["sipsa_abastecimientos<br/>(59,500 filas)"]:::bronze
    silver_sipsa_abastecimientos["sipsa_abastecimientos<br/>(59,500 filas)"]:::silver
    bronze_sipsa_abastecimientos --> silver_sipsa_abastecimientos
    bronze_sipsa_precios["sipsa_precios<br/>(36 filas)"]:::bronze
    silver_sipsa_precios["sipsa_precios<br/>(36 filas)"]:::silver
    bronze_sipsa_precios --> silver_sipsa_precios
    bronze_sipsa_insumos["sipsa_insumos<br/>(92 filas)"]:::bronze
    silver_sipsa_insumos["sipsa_insumos<br/>(92 filas)"]:::silver
    bronze_sipsa_insumos --> silver_sipsa_insumos
    bronze_dane_ipc["dane_ipc<br/>(284 filas)"]:::bronze
    silver_dane_ipc["dane_ipc<br/>(284 filas)"]:::silver
    bronze_dane_ipc --> silver_dane_ipc
    bronze_ideam_pluviometria["ideam_pluviometria<br/>(100 filas)"]:::bronze
    silver_ideam_pluviometria["ideam_pluviometria<br/>(100 filas)"]:::silver
    bronze_ideam_pluviometria --> silver_ideam_pluviometria
    bronze_ideam_telemetria_realtime["ideam_telemetria_realtime<br/>(1,000 filas)"]:::bronze
    silver_ideam_telemetria_realtime["ideam_telemetria_realtime<br/>(1,000 filas)"]:::silver
    bronze_ideam_telemetria_realtime --> silver_ideam_telemetria_realtime
    bronze_dane_csaa["dane_csaa<br/>(22 filas)"]:::bronze
    silver_dane_csaa["dane_csaa<br/>(22 filas)"]:::silver
    bronze_dane_csaa --> silver_dane_csaa
    bronze_doc_webservice_chunks["doc_webservice_chunks<br/>(39 filas)"]:::bronze
    silver_doc_webservice_chunks["doc_webservice_chunks<br/>(39 filas)"]:::silver
    bronze_doc_webservice_chunks --> silver_doc_webservice_chunks
    bronze_landing_leads["landing_leads<br/>(1 filas)"]:::bronze
    silver_landing_leads["landing_leads<br/>(1 filas)"]:::silver
    bronze_landing_leads --> silver_landing_leads
    gold_dim_municipio_divipola["dim_municipio_divipola<br/>(8 filas)"]:::gold
    silver_sipsa_abastecimientos --> gold_dim_municipio_divipola
    silver_sipsa_precios --> gold_dim_municipio_divipola
    silver_sipsa_insumos --> gold_dim_municipio_divipola
    silver_dane_ipc --> gold_dim_municipio_divipola
    silver_ideam_pluviometria --> gold_dim_municipio_divipola
    silver_ideam_telemetria_realtime --> gold_dim_municipio_divipola
    silver_dane_csaa --> gold_dim_municipio_divipola
    silver_doc_webservice_chunks --> gold_dim_municipio_divipola
    silver_landing_leads --> gold_dim_municipio_divipola
    gold_dim_producto_agro["dim_producto_agro<br/>(8 filas)"]:::gold
    silver_sipsa_abastecimientos --> gold_dim_producto_agro
    silver_sipsa_precios --> gold_dim_producto_agro
    silver_sipsa_insumos --> gold_dim_producto_agro
    silver_dane_ipc --> gold_dim_producto_agro
    silver_ideam_pluviometria --> gold_dim_producto_agro
    silver_ideam_telemetria_realtime --> gold_dim_producto_agro
    silver_dane_csaa --> gold_dim_producto_agro
    silver_doc_webservice_chunks --> gold_dim_producto_agro
    silver_landing_leads --> gold_dim_producto_agro
    gold_mart_business_questions["mart_business_questions<br/>(9 filas)"]:::gold
    silver_sipsa_abastecimientos --> gold_mart_business_questions
    silver_sipsa_precios --> gold_mart_business_questions
    silver_sipsa_insumos --> gold_mart_business_questions
    silver_dane_ipc --> gold_mart_business_questions
    silver_ideam_pluviometria --> gold_mart_business_questions
    silver_ideam_telemetria_realtime --> gold_mart_business_questions
    silver_dane_csaa --> gold_mart_business_questions
    silver_doc_webservice_chunks --> gold_mart_business_questions
    silver_landing_leads --> gold_mart_business_questions
```
