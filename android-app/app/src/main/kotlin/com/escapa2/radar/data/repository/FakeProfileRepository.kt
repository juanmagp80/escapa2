package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AirportPreference
import com.escapa2.radar.data.model.TravelProfile
import com.escapa2.radar.data.model.TransportMode
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Development-only source of the couple travel profile.
 *
 * Holds a mutable copy in memory so edits persist during the session without
 * a backend. Mirrors the default profile served by the backend.
 */
@Singleton
class FakeProfileRepository @Inject constructor() : ProfileRepository {

    private var profile: TravelProfile = TravelProfile(
        id = "dev-profile",
        originCity = "Madrid",
        currency = "EUR",
        defaultBudgetEur = 350.0,
        maxDriveMinutes = 240,
        preferredTransport = TransportMode.EITHER,
        interests = listOf("ciudad", "gastronomía"),
        avoidPreferences = listOf("vida nocturna"),
        airports = listOf(
            AirportPreference(
                id = "airport-mad",
                iataCode = "MAD",
                enabled = true,
                transferCostEur = 12.0,
                transferMinutes = 45,
            ),
            AirportPreference(
                id = "airport-agp",
                iataCode = "AGP",
                enabled = false,
                transferCostEur = 25.0,
                transferMinutes = 20,
            ),
        ),
    )

    override suspend fun getProfile(): TravelProfile = profile

    override suspend fun saveProfile(updated: TravelProfile): TravelProfile {
        profile = updated.copy(
            id = profile.id,
            airports = if (updated.airports.isEmpty()) profile.airports else updated.airports,
        )
        return profile
    }
}
