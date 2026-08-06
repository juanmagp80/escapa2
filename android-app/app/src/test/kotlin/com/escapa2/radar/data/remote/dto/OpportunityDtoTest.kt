package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.TransportMode
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
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

    @Test
    fun toDomainMapsInformationalFields() {
        val dto = OpportunityDto(
            id = "opp-3",
            destinationCode = "OPO",
            destinationName = "Porto",
            transportMode = "FLIGHT",
            startAt = "2026-08-21T08:10:00+02:00",
            endAt = "2026-08-23T19:30:00+02:00",
            usefulHours = 40.0,
            totalCostEur = 312.0,
            costPerPersonEur = 156.0,
            costPerNightEur = 156.0,
            costPerUsefulHourEur = 7.8,
            originCity = "Madrid",
            interests = listOf("ciudad", "gastronomía"),
            flightCostEur = 240.0,
            hotelCostEur = 72.0,
            routeCostEur = null,
            bookingUrl = "https://example.com/booking/porto",
        )

        val domain = dto.toDomain()

        assertEquals("Madrid", domain.originCity)
        assertEquals(listOf("ciudad", "gastronomía"), domain.interests)
        assertEquals(240.0, domain.flightCostEur ?: 0.0, 0.0)
        assertEquals(72.0, domain.hotelCostEur ?: 0.0, 0.0)
        assertNull(domain.routeCostEur)
        assertEquals("https://example.com/booking/porto", domain.bookingUrl)
    }
}
