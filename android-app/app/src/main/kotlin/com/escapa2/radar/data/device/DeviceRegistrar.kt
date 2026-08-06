package com.escapa2.radar.data.device

import com.escapa2.radar.data.repository.DeviceRepository
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * Coordinates device registration with the backend based on the user's
 * preference. Exposes the current state as a [StateFlow] so the UI can reflect
 * it without a second source of truth.
 *
 * Enabling registers the device token (idempotent); disabling unregisters it.
 * Registration failures are swallowed: the local preference still reflects the
 * user's intent and the fallback repository keeps the app usable offline.
 */
@Singleton
class DeviceRegistrar @Inject constructor(
    private val repository: DeviceRepository,
    private val tokenProvider: DeviceTokenProvider,
    private val preferences: NotificationPreferences,
    private val scope: CoroutineScope,
) {

    private val _notificationsEnabled = MutableStateFlow(preferences.notificationsEnabled)
    val notificationsEnabled: StateFlow<Boolean> = _notificationsEnabled.asStateFlow()

    /**
     * Syncs with the backend on app start. Safe to call more than once;
     * registration is idempotent by token.
     */
    fun initialize() {
        syncNotifications(preferences.notificationsEnabled)
    }

    fun setNotificationsEnabled(enabled: Boolean) {
        preferences.notificationsEnabled = enabled
        _notificationsEnabled.value = enabled
        syncNotifications(enabled)
    }

    private fun syncNotifications(enabled: Boolean) {
        scope.launch {
            runCatching {
                if (enabled) {
                    repository.register(tokenProvider.token)
                } else {
                    repository.unregister(tokenProvider.token)
                }
            }
        }
    }
}
