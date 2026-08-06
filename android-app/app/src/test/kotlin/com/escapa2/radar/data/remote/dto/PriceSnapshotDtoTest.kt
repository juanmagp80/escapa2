package com.escapa2.radar.data.remote.dto

import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import org.junit.Assert.assertEquals
import org.junit.Test

class PriceSnapshotDtoTest {

    @Test
    fun toDomainMapsFieldsAndProvider() {
        val dto = PriceSnapshotDto(
            id = "snap-1",
            travelOpportunityId = "opp-1",
            totalCostEur = 198.0,
            capturedAt = "2026-08-05T12:00:00Z",
            sourceSummaryJson = buildJsonObject {
                put("provider", JsonPrimitive("mock"))
            },
        )

        val domain = dto.toDomain()

        assertEquals("snap-1", domain.id)
        assertEquals(198.0, domain.totalCostEur ?: 0.0, 0.0)
        assertEquals("2026-08-05T12:00:00Z", domain.capturedAt)
        assertEquals("mock", domain.source)
    }

    @Test
    fun toDomainToleratesMissingOptionalFields() {
        val domain = PriceSnapshotDto(id = "snap-2").toDomain()

        assertEquals("snap-2", domain.id)
        assertEquals(null, domain.totalCostEur)
        assertEquals("", domain.capturedAt)
        assertEquals("", domain.source)
    }
}
