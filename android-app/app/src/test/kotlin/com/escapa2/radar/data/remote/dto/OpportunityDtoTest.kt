package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.TransportMode
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class OpportunityDtoTest {

    @Test
    fun toDomainMapsAllFields() {
        val dto = OpportunityDto(
            id = "opp-1",
            destinationCode = "SVQ",
            destinationName = "Sevilla",
            transportMode = "FLIGHT",
            startAt = "2026-08-14T19:45:00+02:00",
            endAt = "2026-08-16T21:10:00+02:00",
            usefulHours = 30.0,
            totalCostEur = 246.0,
            costPerPersonEur = 123.0,
            costPerNightEur = 123.0,
            costPerUsefulHourEur = 8.20,
            providerVerifiedAt = "2026-08-05T12:00:00Z",
        )

        val domain = dto.toDomain()

        assertEquals("opp-1", domain.id)
        assertEquals("Sevilla", domain.destinationName)
        assertEquals(TransportMode.FLIGHT, domain.transportMode)
        assertEquals(30.0, domain.usefulHours, 0.0)
        assertEquals(246.0, domain.totalCostEur, 0.0)
        assertEquals("2026-08-05T12:00:00Z", domain.verifiedAt)
    }

    @Test
    fun toDomainFallsBackToEitherOnUnknownTransportMode() {
        val dto = OpportunityDto(
            id = "opp-2",
            destinationCode = "X",
            destinationName = "Test",
            transportMode = "TRAIN",
            startAt = "2026-08-14T19:45:00+02:00",
            endAt = "2026-08-16T21:10:00+02:00",
            usefulHours = 10.0,
            totalCostEur = 100.0,
            costPerPersonEur = 50.0,
            costPerNightEur = 50.0,
            costPerUsefulHourEur = 10.0,
        )

        val domain = dto.toDomain()

        assertEquals(TransportMode.EITHER, domain.transportMode)
        assertTrue(domain.verifiedAt.isEmpty())
        assertFalse(domain.destinationName.isBlank())
    }
}
