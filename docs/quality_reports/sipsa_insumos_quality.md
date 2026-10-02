# Reporte de Calidad de Datos: `sipsa_insumos`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T20:02:06.129800  
**Estado General**: ⚠️ WARNING | **Score Global**: `99.9%`  
**Volumen**: 92 filas × 58 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 99.5% | ✅ Óptimo |
| **Uniqueness** | 100.0% | ✅ Óptimo |
| **Validity** | 100.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 99.7% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_fecha | Completeness | `fecha` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_indice_total | Completeness | `indice_total` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_fertilizantes | Completeness | `total_fertilizantes` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_plaguicidas | Completeness | `total_plaguicidas` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_otros | Completeness | `total_otros` | MEDIUM | 0.272 | 0.400 | ✅ PASS |
| null_rate_total_simples | Completeness | `total_simples` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_compuestos | Completeness | `total_compuestos` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_herbicidas | Completeness | `total_herbicidas` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_fungicidas | Completeness | `total_fungicidas` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_insecticidas | Completeness | `total_insecticidas` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_urea_46 | Completeness | `urea_46` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_urea_sulfato | Completeness | `urea_sulfato` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_dap_18_46 | Completeness | `dap_18_46` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_kcl_0_0_60 | Completeness | `kcl_0_0_60` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_sam | Completeness | `sam` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__15_15_15 | Completeness | `_15_15_15` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__25_4_24 | Completeness | `_25_4_24` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__17_6_18_2 | Completeness | `_17_6_18_2` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__18_18_18 | Completeness | `_18_18_18` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__31_8_8 | Completeness | `_31_8_8` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__12_24_12 | Completeness | `_12_24_12` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__13_26_6 | Completeness | `_13_26_6` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__15_4_23 | Completeness | `_15_4_23` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__10_20_30 | Completeness | `_10_20_30` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__28_4_0_6 | Completeness | `_28_4_0_6` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_glifosato | Completeness | `glifosato` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_paraquat | Completeness | `paraquat` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_propanil | Completeness | `propanil` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__2_4_d_picloram | Completeness | `_2_4_d_picloram` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate__2_4_d | Completeness | `_2_4_d` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_aminopiralid_2_4_d | Completeness | `aminopiralid_2_4_d` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_diuron | Completeness | `diuron` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_glufosinato_de_amonio | Completeness | `glufosinato_de_amonio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_picloram | Completeness | `picloram` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_oxadiazon | Completeness | `oxadiazon` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_metsulfuron_metil | Completeness | `metsulfuron_metil` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_pendimetalin | Completeness | `pendimetalin` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_clorotalonil | Completeness | `clorotalonil` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_difenoconazol | Completeness | `difenoconazol` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_mancozeb | Completeness | `mancozeb` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_mancozeb_cimoxanil | Completeness | `mancozeb_cimoxanil` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_azoxistrobin_difenoconazol | Completeness | `azoxistrobin_difenoconazol` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_dimetomorf | Completeness | `dimetomorf` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_tebuconazol_trifloxistrobin | Completeness | `tebuconazol_trifloxistrobin` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_propineb_fluopicolide | Completeness | `propineb_fluopicolide` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_mancozeb_metalaxil_m | Completeness | `mancozeb_metalaxil_m` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_clorpirifos | Completeness | `clorpirifos` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_fipronil | Completeness | `fipronil` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_metomil | Completeness | `metomil` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_tiametoxam_lambdacihalotrina | Completeness | `tiametoxam_lambdacihalotrina` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_abamectina | Completeness | `abamectina` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_imidacloprid | Completeness | `imidacloprid` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_profenofos_cipermetrina | Completeness | `profenofos_cipermetrina` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_cipermetrina | Completeness | `cipermetrina` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_profenofos | Completeness | `profenofos` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_coadyuvantes | Completeness | `total_coadyuvantes` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_reguladores | Completeness | `total_reguladores` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_total_molusquicidas | Completeness | `total_molusquicidas` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| primary_key_uniqueness | Uniqueness | `fecha` | CRITICAL | 0.000 | 0.000 | ✅ PASS |
| range_check_indice_total | Validity | `indice_total` | HIGH | 0.000 | 0.010 | ✅ PASS |
| timeliness_bounds_fecha | Timeliness | `fecha` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| extreme_outliers_iqr_indice_total | Accuracy | `indice_total` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_fertilizantes | Accuracy | `total_fertilizantes` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_plaguicidas | Accuracy | `total_plaguicidas` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_otros | Accuracy | `total_otros` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_simples | Accuracy | `total_simples` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_compuestos | Accuracy | `total_compuestos` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_herbicidas | Accuracy | `total_herbicidas` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_fungicidas | Accuracy | `total_fungicidas` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_insecticidas | Accuracy | `total_insecticidas` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_urea_46 | Accuracy | `urea_46` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_urea_sulfato | Accuracy | `urea_sulfato` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_dap_18_46 | Accuracy | `dap_18_46` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_kcl_0_0_60 | Accuracy | `kcl_0_0_60` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_sam | Accuracy | `sam` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__15_15_15 | Accuracy | `_15_15_15` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__25_4_24 | Accuracy | `_25_4_24` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__17_6_18_2 | Accuracy | `_17_6_18_2` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__18_18_18 | Accuracy | `_18_18_18` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__31_8_8 | Accuracy | `_31_8_8` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__12_24_12 | Accuracy | `_12_24_12` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__13_26_6 | Accuracy | `_13_26_6` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__15_4_23 | Accuracy | `_15_4_23` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__10_20_30 | Accuracy | `_10_20_30` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__28_4_0_6 | Accuracy | `_28_4_0_6` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_glifosato | Accuracy | `glifosato` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_paraquat | Accuracy | `paraquat` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_propanil | Accuracy | `propanil` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__2_4_d_picloram | Accuracy | `_2_4_d_picloram` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr__2_4_d | Accuracy | `_2_4_d` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_aminopiralid_2_4_d | Accuracy | `aminopiralid_2_4_d` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_diuron | Accuracy | `diuron` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_glufosinato_de_amonio | Accuracy | `glufosinato_de_amonio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_picloram | Accuracy | `picloram` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_oxadiazon | Accuracy | `oxadiazon` | LOW | 0.174 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_metsulfuron_metil | Accuracy | `metsulfuron_metil` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_pendimetalin | Accuracy | `pendimetalin` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_clorotalonil | Accuracy | `clorotalonil` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_difenoconazol | Accuracy | `difenoconazol` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_mancozeb | Accuracy | `mancozeb` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_mancozeb_cimoxanil | Accuracy | `mancozeb_cimoxanil` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_azoxistrobin_difenoconazol | Accuracy | `azoxistrobin_difenoconazol` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_dimetomorf | Accuracy | `dimetomorf` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_tebuconazol_trifloxistrobin | Accuracy | `tebuconazol_trifloxistrobin` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_propineb_fluopicolide | Accuracy | `propineb_fluopicolide` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_mancozeb_metalaxil_m | Accuracy | `mancozeb_metalaxil_m` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_clorpirifos | Accuracy | `clorpirifos` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_fipronil | Accuracy | `fipronil` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_metomil | Accuracy | `metomil` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_tiametoxam_lambdacihalotrina | Accuracy | `tiametoxam_lambdacihalotrina` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_abamectina | Accuracy | `abamectina` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_imidacloprid | Accuracy | `imidacloprid` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_profenofos_cipermetrina | Accuracy | `profenofos_cipermetrina` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_cipermetrina | Accuracy | `cipermetrina` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_profenofos | Accuracy | `profenofos` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_coadyuvantes | Accuracy | `total_coadyuvantes` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_reguladores | Accuracy | `total_reguladores` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_total_molusquicidas | Accuracy | `total_molusquicidas` | LOW | 0.000 | 0.050 | ✅ PASS |