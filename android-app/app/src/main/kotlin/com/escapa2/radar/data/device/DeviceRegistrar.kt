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
 * The push token may arrive asynchronously (Firebase) and can be refreshed, so
 * the registrar listens to [DeviceTokenProvider.tokenUpdates] and registers
 * whenever a new token appears while notifications are enabled. The previous
 * token is unregistered before registering a replacement. Registration failures
 * are swallowed: the local preference still reflects the user's intent and the
 * fallback repository keeps the app usable offline.
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

    private var lastRegisteredToken: String? = null

    init {
        scope.launch {
            tokenProvider.tokenUpdates.collect { token ->
                syncToken(token, _notificationsEnabled.value)
            }
        }
    }

    /**
     * Syncs with the backend on app start. Safe to call more than once;
     * registration is idempotent by token.
     */
    fun initialize() {
        _notificationsEnabled.value = preferences.notificationsEnabled
        syncToken(tokenProvider.token, _notificationsEnabled.value)
    }

    fun setNotificationsEnabled(enabled: Boolean) {
        preferences.notificationsEnabled = enabled
        _notificationsEnabled.value = enabled
        syncToken(tokenProvider.token, enabled)
    }

    private fun syncToken(token: String, enabled: Boolean) {
        if (token.isEmpty()) return
        if (enabled && token == lastRegisteredToken) return
        scope.launch {
            runCatching {
                if (enabled) {
                    lastRegisteredToken?.takeIf { it != token }?.let { previous ->
                        repository.unregister(previous)
                    }
                    repository.register(token)
                    lastRegisteredToken = token
                } else {
                    repository.unregister(token)
                    lastRegisteredToken = null
                }
            }
        }
    }
}
