package com.escapa2.radar.ui.profile

import androidx.lifecycle.ViewModel
import com.escapa2.radar.data.device.DeviceRegistrar
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.StateFlow

/**
 * Thin bridge between the Perfil screen and [DeviceRegistrar] so the switch
 * reflects the persisted notification preference and toggles device
 * registration with the backend.
 */
@HiltViewModel
class NotificationSettingsViewModel @Inject constructor(
    private val registrar: DeviceRegistrar,
) : ViewModel() {

    val notificationsEnabled: StateFlow<Boolean> = registrar.notificationsEnabled

    fun setNotificationsEnabled(enabled: Boolean) = registrar.setNotificationsEnabled(enabled)
}
