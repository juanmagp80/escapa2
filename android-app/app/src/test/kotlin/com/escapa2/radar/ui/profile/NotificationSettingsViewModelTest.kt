package com.escapa2.radar.ui.profile

import com.escapa2.radar.data.device.DeviceRegistrar
import com.escapa2.radar.data.device.DeviceTokenProvider
import com.escapa2.radar.data.device.NotificationPreferences
import com.escapa2.radar.data.repository.FakeDeviceRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class NotificationSettingsViewModelTest {

    @Test
    fun exposesRegistrarState() = runTest {
        val registrar = DeviceRegistrar(
            repository = FakeDeviceRepository(),
            tokenProvider = FakeTokenProvider(),
            preferences = FakePreferences(),
            scope = CoroutineScope(SupervisorJob() + this.coroutineContext),
        )
        val viewModel = NotificationSettingsViewModel(registrar)

        assertFalse(viewModel.notificationsEnabled.value)

        viewModel.setNotificationsEnabled(true)
        advanceUntilIdle()

        assertTrue(viewModel.notificationsEnabled.value)
        assertEquals(true, viewModel.notificationsEnabled.value)
    }

    private class FakeTokenProvider : DeviceTokenProvider {
        override val token: String = "android-viewmodel-token"
        override val tokenUpdates: Flow<String> = flowOf(token)
    }

    private class FakePreferences : NotificationPreferences {
        override var notificationsEnabled: Boolean = false
    }
}
