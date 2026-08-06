package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.DeviceRegistration

/**
 * Tries the backend device endpoints first and falls back to the local
 * in-memory registry when the backend is unreachable, so enabling
 * notifications never crashes the app while offline.
 */
class FallbackDeviceRepository(
    private val remote: DeviceRepository,
    private val local: DeviceRepository,
) : DeviceRepository {

    override suspend fun register(token: String): DeviceRegistration =
        try {
            remote.register(token)
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.register(token)
            } else {
                throw throwable
            }
        }

    override suspend fun unregister(token: String) {
        try {
            remote.unregister(token)
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.unregister(token)
            } else {
                throw throwable
            }
        }
    }
}
