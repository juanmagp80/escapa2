package com.escapa2.radar.data.device

/**
 * Provides the stable identifier sent to the backend when registering this
 * device for push notifications.
 *
 * Until Firebase Messaging is configured the token is a per-install generated
 * identifier. When FCM lands, the implementation should return the real
 * Firebase token so notifications can reach the device (AGENTS.md Fase 4).
 */
interface DeviceTokenProvider {

    val token: String
}
