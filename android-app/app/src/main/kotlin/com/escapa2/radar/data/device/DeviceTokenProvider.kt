package com.escapa2.radar.data.device

import kotlinx.coroutines.flow.Flow

/**
 * Provides the push token registered with the backend for this device.
 *
 * [token] is the current token and [tokenUpdates] emits the token whenever it
 * changes (including the initial one once available), so the registrar can
 * re-register on refresh. The real implementation returns the Firebase
 * Messaging token; fakes are used in tests.
 */
interface DeviceTokenProvider {

    val token: String

    val tokenUpdates: Flow<String>
}
