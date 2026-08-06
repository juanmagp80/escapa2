package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.DeviceRegistration

/**
 * Registers and removes the current device with the notification backend.
 *
 * Registration is idempotent by token: calling [register] twice with the same
 * token must not create duplicates.
 */
interface DeviceRepository {

    suspend fun register(token: String): DeviceRegistration

    suspend fun unregister(token: String)
}
