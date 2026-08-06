package com.escapa2.radar.data.remote.dto

import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class DailyReportDtoTest {

    private val json = Json { ignoreUnknownKeys = true }

    @Test
    fun decodesDailyReportWithSnakeCaseFields() {
        val payload = """
            {
              "headline": "2 de 2 viajes vigilados bajaron de precio",
              "summary": "Los precios verificados hoy bajan.",
              "entries": [
                {
                  "watch_name": "Porto en avión",
                  "destination": "Porto",
                  "change_eur": 16.0,
                  "change_percent": 4.9,
                  "is_new_low": true,
                  "within_budget": true,
                  "recommendation": "Nuevo mínimo registrado",
                  "confidence": "HIGH"
                }
              ],
              "warnings": ["Los precios pueden cambiar."],
              "generated_by_ai": false
            }
        """.trimIndent()

        val dto = json.decodeFromString<DailyReportResponseDto>(payload)

        assertEquals("2 de 2 viajes vigilados bajaron de precio", dto.headline)
        assertEquals(1, dto.entries.size)
        val entry = dto.entries[0]
        assertEquals("Porto en avión", entry.watchName)
        assertEquals("Porto", entry.destination)
        assertEquals(16.0, entry.changeEur!!, 0.001)
        assertEquals(4.9, entry.changePercent!!, 0.001)
        assertTrue(entry.isNewLow)
        assertEquals(true, entry.withinBudget)
        assertEquals("Nuevo mínimo registrado", entry.recommendation)
        assertEquals("HIGH", entry.confidence)
        assertEquals(1, dto.warnings.size)
        assertFalse(dto.generatedByAi)
    }

    @Test
    fun decodesDailyReportWithMissingOptionalFields() {
        val payload = """
            {
              "headline": "Sin cambios importantes",
              "summary": "Los precios no presentan bajadas.",
              "entries": [
                {
                  "watch_name": "Galicia en coche",
                  "destination": "Galicia",
                  "is_new_low": false,
                  "recommendation": "Sin cambios significativos",
                  "confidence": "HIGH"
                }
              ],
              "warnings": [],
              "generated_by_ai": true
            }
        """.trimIndent()

        val dto = json.decodeFromString<DailyReportResponseDto>(payload)

        val entry = dto.entries[0]
        assertNull(entry.changeEur)
        assertNull(entry.changePercent)
        assertNull(entry.withinBudget)
        assertFalse(entry.isNewLow)
        assertTrue(dto.generatedByAi)
    }
}
