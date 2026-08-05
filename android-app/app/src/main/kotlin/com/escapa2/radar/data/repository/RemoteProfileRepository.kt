package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.TravelProfile
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.remote.dto.toDomain
import com.escapa2.radar.data.remote.dto.toInputDto
import com.escapa2.radar.data.remote.dto.toUpdateDto

/**
 * Repository backed by the backend profile endpoints.
 *
 * The backend serves airports on a separate route, so [getProfile] joins both
 * before returning the domain model.
 */
class RemoteProfileRepository(
    private val api: Escapa2Api,
) : ProfileRepository {

    override suspend fun getProfile(): TravelProfile {
        val airports = api.getAirports().map { it.toDomain() }
        return api.getProfile().toDomain().copy(airports = airports)
    }

    override suspend fun saveProfile(profile: TravelProfile): TravelProfile {
        val updated = api.updateProfile(profile.toUpdateDto()).toDomain()
        val airports = api.replaceAirports(profile.airports.map { it.toInputDto() })
            .map { it.toDomain() }
        return updated.copy(airports = airports)
    }
}
