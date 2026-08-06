package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.DeviceRegistration
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * In-memory device registry used during development and as the local fallback.
 * Registration is idempotent by token.
 */
@Singleton
class FakeDeviceRepository @Inject constructor() : DeviceRepository {

    private val devices = mutableMapOf<String, DeviceRegistration>()

    val registeredTokens: Set<String>
        get() = devices.keys

    override suspend fun register(token: String): DeviceRegistration {
        devices[token]?.let { return it }
        return DeviceRegistration(
            id = "device-${UUID.randomUUID()}",
            userId = "dev-user",
            token = token,
            platform = "android",
        ).also { devices[token] = it }
    }

    override suspend fun unregister(token: String) {
        devices.remove(token)
    }
}
