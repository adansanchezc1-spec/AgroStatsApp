"""Contratos de Calidad y Validación de Esquemas (Quality Gates).
Fase PDCO: DEVELOPMENT | Estándar: DAMA-DMBOK 2 (Data Quality) / ISO/IEC 25010
Modelos de validación con restricciones de dominio y límites físicos.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


class ValidationError(Exception):
    """Excepción para violaciones de contratos de datos."""
    pass


class EVARecordContract:
    """Contrato de validación para registros de Evaluaciones Agropecuarias (UPRA/EVA)."""

    @classmethod
    def validate(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []

        # Departamento y Municipio
        cod_dep = str(record.get("c_d_dep") or record.get("codigo_departamento") or "").strip()
        cod_mun = str(record.get("c_d_mun") or record.get("codigo_municipio") or "").strip()
        if not cod_mun:
            errors.append("codigo_municipio no puede estar vacío")

        # Año
        try:
            anio = int(float(record.get("a_o") or record.get("anio") or 0))
            if not (2000 <= anio <= 2030):
                errors.append(f"anio ({anio}) fuera de rango válido [2000, 2030]")
        except (ValueError, TypeError):
            errors.append(f"anio inválido: {record.get('a_o') or record.get('anio')}")
            anio = 0

        # Cultivo
        cultivo = str(record.get("cultivo") or "").strip()
        if not cultivo:
            errors.append("cultivo no puede estar vacío")

        # Área sembrada, cosechada, producción y rendimiento
        try:
            area_sembrada = float(record.get("rea_sembrada_ha") or record.get("area_sembrada") or 0.0)
            if area_sembrada < 0:
                errors.append(f"area_sembrada ({area_sembrada}) no puede ser negativa")
        except (ValueError, TypeError):
            errors.append("area_sembrada no numérica")
            area_sembrada = 0.0

        try:
            area_cosechada = float(record.get("rea_cosechada_ha") or record.get("area_cosechada") or 0.0)
            if area_cosechada < 0:
                errors.append(f"area_cosechada ({area_cosechada}) no puede ser negativa")
            elif area_sembrada > 0 and area_cosechada > (area_sembrada * 1.15):
                errors.append(f"area_cosechada ({area_cosechada}) excede tolerancia sobre area_sembrada ({area_sembrada})")
        except (ValueError, TypeError):
            errors.append("area_cosechada no numérica")
            area_cosechada = 0.0

        try:
            produccion = float(record.get("producci_n_t") or record.get("produccion") or 0.0)
            if produccion < 0:
                errors.append(f"produccion ({produccion}) no puede ser negativa")
        except (ValueError, TypeError):
            errors.append("produccion no numérica")
            produccion = 0.0

        try:
            rendimiento = float(record.get("rendimiento_t_ha") or record.get("rendimiento") or 0.0)
            if rendimiento < 0:
                errors.append(f"rendimiento ({rendimiento}) no puede ser negativo")
        except (ValueError, TypeError):
            errors.append("rendimiento no numérico")
            rendimiento = 0.0

        if errors:
            raise ValidationError("; ".join(errors))

        return {
            "codigo_departamento": cod_dep,
            "codigo_municipio": cod_mun,
            "anio": anio,
            "cultivo": cultivo.upper(),
            "area_sembrada": area_sembrada,
            "area_cosechada": area_cosechada,
            "produccion": produccion,
            "rendimiento": rendimiento,
        }


class IDEAMClimaContract:
    """Contrato de validación para mediciones meteorológicas de IDEAM."""

    @classmethod
    def validate(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []

        estacion = str(record.get("codigoestacion") or record.get("codigo_estacion") or record.get("estacion") or "").strip()
        if not estacion:
            errors.append("codigo_estacion no puede estar vacío")

        fecha = str(record.get("fechaobservacion") or record.get("fecha") or "").strip()
        if not fecha:
            errors.append("fecha no puede estar vacía")

        # Valor y límites físicos
        raw_val = record.get("valorobservado") or record.get("valor")
        try:
            valor = float(raw_val)
            descripcion = str(record.get("descripcionsensor") or record.get("variable") or "").lower()

            if "precipitaci" in descripcion or "lluvia" in descripcion or "pluvio" in descripcion:
                if valor < 0.0:
                    errors.append(f"precipitacion ({valor} mm) no puede ser negativa")
                elif valor > 600.0:
                    errors.append(f"precipitacion ({valor} mm) supera límite físico diario (600 mm)")

            elif "temperatura" in descripcion:
                if not (-15.0 <= valor <= 60.0):
                    errors.append(f"temperatura ({valor} °C) fuera de límites físicos [-15, 60]")

            elif "radiaci" in descripcion:
                if valor < 0.0:
                    errors.append(f"radiacion solar ({valor}) no puede ser negativa")

        except (ValueError, TypeError):
            errors.append(f"valor meteorológico no numérico: {raw_val}")
            valor = 0.0

        if errors:
            raise ValidationError("; ".join(errors))

        return {
            "codigo_estacion": estacion,
            "fecha": fecha,
            "valor": valor,
        }


class SIPSAPrecioContract:
    """Contrato de validación para series de precios mayoristas e insumos (DANE/SIPSA)."""

    @classmethod
    def validate(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []

        articulo = str(record.get("articulo") or record.get("producto") or "").strip()
        if not articulo:
            errors.append("articulo no puede estar vacío")

        # Mes
        try:
            mes = int(float(record.get("mes") or 0))
            if not (1 <= mes <= 12):
                errors.append(f"mes ({mes}) debe estar en rango [1, 12]")
        except (ValueError, TypeError):
            errors.append(f"mes no numérico: {record.get('mes')}")
            mes = 0

        # Año
        try:
            anio = int(float(record.get("anio") or record.get("a_o") or 0))
            if not (2000 <= anio <= 2030):
                errors.append(f"anio ({anio}) fuera de rango válido [2000, 2030]")
        except (ValueError, TypeError):
            errors.append(f"anio no numérico: {record.get('anio')}")
            anio = 0

        # Precio
        try:
            precio = float(record.get("preciopromedio") or record.get("precio_promedio") or record.get("precio") or 0.0)
            if precio <= 0.0:
                errors.append(f"precio ({precio}) debe ser estrictamente mayor a 0")
        except (ValueError, TypeError):
            errors.append("precio no numérico")
            precio = 0.0

        if errors:
            raise ValidationError("; ".join(errors))

        return {
            "articulo": articulo.upper(),
            "anio": anio,
            "mes": mes,
            "precio": precio,
        }


class ICAPecuarioContract:
    """Contrato de validación para inventario pecuario y movilización animal (ICA)."""

    @classmethod
    def validate(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []

        cod_mun = str(record.get("cod_municipio") or record.get("col_0") or "").strip()
        if not cod_mun:
            errors.append("codigo_municipio no puede estar vacío")

        especie = str(record.get("especie") or record.get("col_1") or "").strip()
        if not especie:
            errors.append("especie no puede estar vacía")

        # Total animales
        try:
            total_animales = int(float(record.get("total_animales") or record.get("col_3") or 0))
            if total_animales < 0:
                errors.append(f"total_animales ({total_animales}) no puede ser negativo")
        except (ValueError, TypeError):
            errors.append("total_animales no numérico")
            total_animales = 0

        if errors:
            raise ValidationError("; ".join(errors))

        return {
            "codigo_municipio": cod_mun,
            "especie": especie.upper(),
            "total_animales": total_animales,
        }
