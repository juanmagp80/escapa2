package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.AirportPreference
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.model.TravelProfile
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ProfileDtoTest {

    @Test
    fun toDomainMapsSnakeCaseFields() {
        val dto = ProfileDto(
            id = "profile-1",
            originCity = "Madrid",
            currency = "EUR",
            defaultBudgetEur = 350.0,
            maxDriveMinutes = 240,
            preferredTransport = "FLIGHT",
            interests = listOf("ciudad"),
            avoidPreferences = listOf("vida nocturna"),
        )

        val domain = dto.toDomain()

        assertEquals("profile-1", domain.id)
        assertEquals("Madrid", domain.originCity)
        assertEquals(350.0, domain.defaultBudgetEur ?: 0.0, 0.0)
        assertEquals(240, domain.maxDriveMinutes ?: 0)
        assertEquals(TransportMode.FLIGHT, domain.preferredTransport)
        assertEquals(listOf("ciudad"), domain.interests)
        assertTrue(domain.airports.isEmpty())
    }

    @Test
    fun toDomainFallsBackToEitherOnUnknownTransport() {
        val dto = ProfileDto(
            id = "profile-2",
            originCity = "Barcelona",
            currency = "EUR",
            preferredTransport = "TRAIN",
        )

        assertEquals(TransportMode.EITHER, dto.toDomain().preferredTransport)
    }

    @Test
    fun airportDtoToDomainUsesIataAsId() {
        val dto = AirportPreferenceDto(
            iataCode = "MAD",
            enabled = false,
            transferCostEur = 12.0,
            transferMinutes = 45,
        )

        val domain = dto.toDomain()

        assertEquals("MAD", domain.id)
        assertEquals("MAD", domain.iataCode)
        assertFalse(domain.enabled)
        assertEquals(12.0, domain.transferCostEur ?: 0.0, 0.0)
        assertEquals(45, domain.transferMinutes ?: 0)
    }

    @Test
    fun toUpdateDtoRoundTripsProfileFields() {
        val profile = TravelProfile(
            id = "profile-3",
            originCity = "Sevilla",
            currency = "EUR",
            defaultBudgetEur = 400.0,
            maxDriveMinutes = 180,
            preferredTransport = TransportMode.CAR,
            interests = listOf("playa"),
            avoidPreferences = emptyList(),
            airports = emptyList(),
        )

        val dto = profile.toUpdateDto()

        assertEquals("Sevilla", dto.originCity)
        assertEquals(400.0, dto.defaultBudgetEur ?: 0.0, 0.0)
        assertEquals("CAR", dto.preferredTransport)
        assertEquals(listOf("playa"), dto.interests)
    }

    @Test
    fun airportRoundTripsThroughInputDto() {
        val airport = AirportPreference(
            id = "MAD",
            iataCode = "MAD",
            enabled = true,
            transferCostEur = 10.0,
            transferMinutes = 30,
        )

        val dto = airport.toInputDto()

        assertEquals("MAD", dto.iataCode)
        assertTrue(dto.enabled)
        assertEquals(10.0, dto.transferCostEur ?: 0.0, 0.0)
        assertEquals(30, dto.transferMinutes ?: 0)
    }
}
