package com.escapa2.radar.data.remote.dto

import org.junit.Assert.assertEquals
import org.junit.Test

class WatchRunResultDtoTest {

    @Test
    fun toDomainMapsTimestampsMatchesAndAlerts() {
        val dto = WatchRunResultDto(
            lastRunAt = "2026-08-06T12:00:00Z",
            nextRunAt = "2026-08-07T12:00:00Z",
            matchedOpportunities = listOf(
                MatchedOpportunityDto(
                    id = "opp-1",
                    destinationName = "Sevilla",
                    totalCostEur = 246.0,
                ),
            ),
            alerts = listOf(
                WatchRunAlertDto(rule = "new_low", message = "Nuevo mínimo histórico: 246 EUR"),
                WatchRunAlertDto(rule = "percent_drop", message = "Bajada del 14.4%"),
            ),
        )

        val domain = dto.toDomain()

        assertEquals("2026-08-06T12:00:00Z", domain.lastRunAt)
        assertEquals("2026-08-07T12:00:00Z", domain.nextRunAt)
        assertEquals(1, domain.matchedCount)
        assertEquals(
            listOf("Nuevo mínimo histórico: 246 EUR", "Bajada del 14.4%"),
            domain.alerts,
        )
    }

    @Test
    fun toDomainToleratesMissingFields() {
        val domain = WatchRunResultDto().toDomain()

        assertEquals("", domain.lastRunAt)
        assertEquals(0, domain.matchedCount)
        assertEquals(emptyList<String>(), domain.alerts)
    }

    @Test
    fun toDomainSkipsAlertsWithoutMessage() {
        val dto = WatchRunResultDto(
            alerts = listOf(WatchRunAlertDto(rule = "new_low", message = null)),
        )

        assertEquals(emptyList<String>(), dto.toDomain().alerts)
    }
}
