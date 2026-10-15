import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from chaskiwasi.contract import BaseExtractionConfig


class AsientoPresentacion(BaseModel):
    numero_titulo: Optional[str] = Field(default=None, description="Número de título de presentación en SUNARP (ej: 2010-00036232).")
    fecha_presentacion: Optional[str] = Field(default=None, description="Fecha en la que se presentó el título.")
    tomo_diario: Optional[str] = Field(default=None, description="Tomo o diario registral (ej: Tomo Diario 0030).")
    arancel: Optional[float] = Field(default=None, description="Monto del arancel pagado por el título.")
    registrador_publico: Optional[str] = Field(default=None, description="Nombre del registrador público a cargo.")


class ParteInvolucrada(BaseModel):
    nombre: str = Field(..., description="Nombre completo de la persona natural o jurídica (ej: HOSTAL AYAPALLECK MUCHIK E.I.R.L.).")
    tipo_rol: str = Field(..., description="Rol jurídico en el acto: VENDEDOR, COMPRADOR, ACREEDOR, DEUDOR, DEMANDANTE, DEMANDADO, PROPIETARIO.")
    documento_identidad: Optional[str] = Field(default=None, description="Número de DNI o RUC de la parte.")
    estado_civil: Optional[str] = Field(default=None, description="Estado civil registrado (ej: Casado(a), Soltero(a)).")


class DetalleActo(BaseModel):
    monto: Optional[float] = Field(default=None, description="Monto monetario del acto (ej: 88000.00).")
    moneda: str = Field(default="USD", description="Moneda de la transacción: USD o S/.")
    numero_expediente: Optional[str] = Field(default=None, description="Número de expediente judicial para embargos o procesos (ej: 00804-2008-0-1706-JR-LA-04).")
    juzgado: Optional[str] = Field(default=None, description="Nombre del juzgado o entidad judicial interviniente.")
    juez: Optional[str] = Field(default=None, description="Nombre del juez a cargo.")
    notaria_o_institucion: Optional[str] = Field(default=None, description="Nombre del notario o institución (ej: Notario Antonio Enrique Vera Méndez o COFOPRI).")
    instrumento_publico: Optional[str] = Field(default=None, description="Documento oficial o escritura pública (ej: Escritura Pública N° 1893).")


class AsientoRegistral(BaseModel):
    numero_asiento: str = Field(..., description="Número del asiento registral (ej: 00001, 00002, D00005, C00001).")
    rubro: str = Field(..., description="Rubro registral (ej: TITULOS DE DOMINIO, GRAVAMENES Y CARGAS, DESCRIPCION DEL PREDIO).")
    descripcion_acto: str = Field(..., description="Descripción jurídica del acto (ej: COMPRAVENTA, HIPOTECA, MEDIDA CAUTELAR DE EMBARGO).")
    partes: List[ParteInvolucrada] = Field(default_factory=list, description="Lista de partes naturales o jurídicas involucradas en el asiento.")
    detalles: Optional[DetalleActo] = Field(default=None, description="Detalles económicos, notariales o judiciales del acto.")
    asiento_presentacion: Optional[AsientoPresentacion] = Field(default=None, description="Datos del título de presentación de SUNARP asociado.")
    texto_original: Optional[str] = Field(default=None, description="Extracto o texto original del asiento para fines de auditoría.")


class LinderoColindancia(BaseModel):
    lindo_o_frontera: Optional[str] = Field(default=None, description="Orientación física: FRENTE, DERECHA, IZQUIERDA o FONDO.")
    medidas: Optional[str] = Field(default=None, description="Medida lineal lineal (ej: 33.57 ML, 20.48 ML).")
    colindancia: Optional[str] = Field(default=None, description="Descripción del colindante o vía adyacente (ej: AV. PERU, LOTE 2).")


class SunarpSchema(BaseModel):
    partida_registral: str = Field(..., description="Número único de la partida registral o ficha (ej: 02027517, P24007506).")
    zona_registral: str = Field(..., description="Zona registral de SUNARP (ej: ZONA REGISTRAL N° II - SEDE CHICLAYO).")
    oficina_registral: str = Field(..., description="Oficina registral de SUNARP (ej: OFICINA REGISTRAL CHICLAYO).")
    ubicacion_detallada: Optional[str] = Field(default=None, description="Ubicación física detallada del inmueble.")
    departamento: Optional[str] = Field(default=None, description="Departamento geográfico (ej: HUANCAVELICA, LAMBAYEQUE).")
    provincia: Optional[str] = Field(default=None, description="Provincia geográfica.")
    distrito: Optional[str] = Field(default=None, description="Distrito geográfico.")
    uso_predio: Optional[str] = Field(default=None, description="Uso asignado al predio (ej: VIVIENDA, COMERCIO, AGRICOLA).")
    situacion_actual: Optional[str] = Field(default=None, description="Situación jurídica actual (ej: CARGA, LIBRE DE GRAVAMENES).")
    estado_partida: Optional[str] = Field(default=None, description="Estado de vigencia (ej: PARTIDA ACTIVA).")
    antecedente_registral: Optional[str] = Field(default=None, description="Partida o tomo de antecedentes registrales.")
    area_total_m2: Optional[float] = Field(default=None, description="Área total del predio en metros cuadrados (ej: 526.2).")
    medidas_y_colindancias: List[LinderoColindancia] = Field(default_factory=list, description="Lista de linderos y colindancias del inmueble.")
    historial_asientos: List[AsientoRegistral] = Field(default_factory=list, description="Historial completo y ordenado de los asientos registrales.")


class SunarpConfig(BaseExtractionConfig):
    
    @property
    def model_class(self):
        return SunarpSchema
        
    @property
    def model_name(self) -> str:
        # Se asigna un modelo de alta capacidad analítica y de contexto
        return "gemini-2.5-flash"

    @property
    def palabras_clave(self) -> List[str]:
        return [
            "sunarp", "registros públicos", "partida registral", "asiento", 
            "gravamen", "hipoteca", "embargo", "propietario", "predial",
            "tomo", "fichas", "rubro", "dominio", "inscripción"
        ]

    @property
    def prompt_extraccion(self) -> str:
        return (
            "Actúa como un abogado especialista en derecho registral inmobiliario peruano y auditor senior "
            "de partidas registrales de la SUNARP. Tu objetivo es realizar un Estudio de Títulos completo y de "
            "nivel industrial extrayendo toda la información detallada del documento o texto de la partida registral.\n\n"
            "INSTRUCCIONES CRÍTICAS:\n"
            "1. No inventes ni supongas datos que no estén explícitamente en el texto.\n"
            "2. partida_registral, zona_registral y oficina_registral son obligatorios.\n"
            "3. historial_asientos: Extrae de forma cronológica y ordenada cada asiento registral (ej. 00001, C00001, D00005), indicando su rubro (TITULOS DE DOMINIO, GRAVAMENES Y CARGAS, etc.) y descripción del acto.\n"
            "4. partes: Para cada asiento, identifica con precisión a las personas naturales o jurídicas involucradas y su rol exacto (VENDEDOR, COMPRADOR, ACREEDOR, DEUDOR, DEMANDANTE, DEMANDADO, PROPIETARIO).\n"
            "5. detalles y asiento_presentacion: Extrae montos, monedas, números de títulos, fechas, juzgados, expedientes judiciales, notarias e instrumentos públicos cuando el asiento los mencione.\n"
            "6. medidas_y_colindancias: Captura el perímetro, linderos y colindancias exactas descritas en la descripción del predio.\n"
            "7. Sé exhaustivo: Ningún gravamen, carga, embargo o transferencia de dominio debe quedar fuera."
        )

    PATRON_PARTIDA = r"\b(?:P\d{8}|\d{8})\b"

    @property
    def campos_requeridos(self) -> List[str]:
        return [
            "partida_registral",
            "zona_registral",
            "oficina_registral",
            "historial_asientos"
        ]

    def extraer_identificador(self, texto: str) -> str:
        if not texto:
            return "No detectado"

        match = re.search(self.PATRON_PARTIDA, texto, re.IGNORECASE)
        if match:
            return match.group(0).upper()

        return "No detectado"

    def fusionar_datos(self, scraper_metadata: Dict[str, Any], ai_extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Reglas de negocio empresariales para unificar los metadatos del scraper y el análisis profundo de IA."""
        registro_unificado = dict(scraper_metadata)
        datos_ia = ai_extraction_result.get("datos_extraidos", {})
        
        partida_ia = datos_ia.get("partida_registral")
        if partida_ia and partida_ia != "No detectado":
            registro_unificado["partida_registral"] = partida_ia

        # Estructura final unificada bajo el estándar de Estudio de Títulos detallado
        registro_unificado["estudio_titulos_sunarp"] = {
            "zona_registral": datos_ia.get("zona_registral"),
            "oficina_registral": datos_ia.get("oficina_registral"),
            "ubicacion_detallada": datos_ia.get("ubicacion_detallada"),
            "ubicacion_geografica": {
                "departamento": datos_ia.get("departamento"),
                "provincia": datos_ia.get("provincia"),
                "distrito": datos_ia.get("distrito")
            },
            "caracteristicas_predio": {
                "uso_predio": datos_ia.get("uso_predio"),
                "area_total_m2": datos_ia.get("area_total_m2"),
                "situacion_actual": datos_ia.get("situacion_actual"),
                "estado_partida": datos_ia.get("estado_partida"),
                "antecedente_registral": datos_ia.get("antecedente_registral")
            },
            "medidas_y_colindancias": datos_ia.get("medidas_y_colindancias", []),
            "historial_asientos": datos_ia.get("historial_asientos", []),
            "auditoria_ia": {
                "campos_faltantes": ai_extraction_result.get("campos_faltantes", []),
                "completado_exitosamente": ai_extraction_result.get("completado_exitosamente", False)
            }
        }
        
        return registro_unificado