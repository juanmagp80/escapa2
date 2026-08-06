package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.DeviceRegistration
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.remote.dto.RegisterDeviceRequestDto
import com.escapa2.radar.data.remote.dto.toDomain

/**
 * Repository backed by the backend device registration endpoints.
 */
class RemoteDeviceRepository(
    private val api: Escapa2Api,
) : DeviceRepository {

    override suspend fun register(token: String): DeviceRegistration =
        api.registerDevice(RegisterDeviceRequestDto(token = token)).toDomain()

    override suspend fun unregister(token: String) {
        api.unregisterDevice(token)
    }
}
