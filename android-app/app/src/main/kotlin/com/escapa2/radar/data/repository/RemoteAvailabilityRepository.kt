package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AvailabilityWindow
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.remote.dto.toDomain

/**
 * Repository backed by the backend availability endpoints.
 */
class RemoteAvailabilityRepository(
    private val api: Escapa2Api,
) : AvailabilityRepository {

    override suspend fun getWindows(): List<AvailabilityWindow> =
        api.getAvailabilityWindows().map { it.toDomain() }
}
