package com.escapa2.radar.data.remote.dto

import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.doubleOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.put
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SearchWatchDtoTest {

    @Test
    fun toDomainMapsFieldsAndDerivedValues() {
        val dto = SearchWatchDto(
            id = "watch-1",
            name = "Porto en avión",
            status = "ACTIVE",
            criteriaJson = buildJsonObject {
                put("initial_price_eur", JsonPrimitive(312.0))
            },
            alertRulesJson = buildJsonObject {
                put("rules", JsonArray(listOf(JsonPrimitive("Nuevo mínimo histórico"))))
            },
            lastRunAt = "2026-08-05T12:00:00Z",
            nextRunAt = "2026-08-06T12:00:00Z",
        )

        val domain = dto.toDomain()

        assertEquals("watch-1", domain.id)
        assertEquals("Porto en avión", domain.name)
        assertEquals("ACTIVE", domain.status)
        assertEquals("2026-08-05T12:00:00Z", domain.lastRunAt)
        assertEquals(312.0, domain.minRecordedEur ?: 0.0, 0.0)
        assertEquals(listOf("Nuevo mínimo histórico"), domain.alertRules)
        assertTrue(domain.priceHistory.isEmpty())
        assertNull(domain.changeSinceYesterdayEur)
    }

    @Test
    fun toDomainToleratesMissingCriteria() {
        val dto = SearchWatchDto(
            id = "watch-2",
            name = "Galicia en coche",
            status = "PAUSED",
        )

        val domain = dto.toDomain()

        assertNull(domain.minRecordedEur)
        assertTrue(domain.alertRules.isEmpty())
        assertEquals("", domain.lastRunAt)
    }

    @Test
    fun initialPriceCriteriaRoundTrips() {
        val criteria = initialPriceCriteria(246.0)
        val value = criteria["initial_price_eur"]?.jsonPrimitive?.doubleOrNull

        assertEquals(246.0, value ?: 0.0, 0.0)
    }

    @Test
    fun defaultAlertRulesContainsMention() {
        val rules = defaultAlertRules()
        val values = rules["rules"]?.jsonArray?.map { it.jsonPrimitive.content }

        assertTrue(values?.contains("Nuevo mínimo histórico") == true)
    }
}
