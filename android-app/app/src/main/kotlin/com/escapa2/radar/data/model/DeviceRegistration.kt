package com.escapa2.radar.data.model

/**
 * A push device registered for the current user.
 *
 * The backend stores the token so the radar can send notifications when a
 * watched trip triggers an alert. The token is a stable, per-install
 * identifier; it will become a real Firebase Messaging token once FCM is
 * configured (AGENTS.md Fase 4).
 */
data class DeviceRegistration(
    val id: String,
    val userId: String,
    val token: String,
    val platform: String,
)
