package com.escapa2.radar.data.device

import com.escapa2.radar.data.repository.DeviceRepository
import com.escapa2.radar.data.repository.FakeDeviceRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class DeviceRegistrarTest {

    private class FakeTokenProvider(override val token: String) : DeviceTokenProvider

    private class FakeNotificationPreferences : NotificationPreferences {
        override var notificationsEnabled: Boolean = false
    }

    @Test
    fun enablingRegistersDeviceAndPersistsPreference() = runTest {
        val repository = FakeDeviceRepository()
        val preferences = FakeNotificationPreferences()
        val registrar = registrar(repository, preferences)

        registrar.setNotificationsEnabled(true)
        advanceUntilIdle()

        assertTrue(registrar.notificationsEnabled.value)
        assertTrue(preferences.notificationsEnabled)
        assertEquals(setOf("android-test-token"), repository.registeredTokens)
    }

    @Test
    fun disablingUnregistersDevice() = runTest {
        val repository = FakeDeviceRepository()
        val preferences = FakeNotificationPreferences().apply { notificationsEnabled = true }
        val registrar = registrar(repository, preferences)

        registrar.initialize()
        advanceUntilIdle()
        assertEquals(setOf("android-test-token"), repository.registeredTokens)

        registrar.setNotificationsEnabled(false)
        advanceUntilIdle()

        assertFalse(registrar.notificationsEnabled.value)
        assertFalse(preferences.notificationsEnabled)
        assertTrue(repository.registeredTokens.isEmpty())
    }

    @Test
    fun initializeSeedsStateFromPreference() = runTest {
        val preferences = FakeNotificationPreferences().apply { notificationsEnabled = true }
        val registrar = registrar(FakeDeviceRepository(), preferences)

        assertTrue(registrar.notificationsEnabled.value)
    }

    private fun CoroutineScope.registrar(
        repository: DeviceRepository,
        preferences: NotificationPreferences,
    ): DeviceRegistrar = DeviceRegistrar(
        repository = repository,
        tokenProvider = FakeTokenProvider("android-test-token"),
        preferences = preferences,
        scope = CoroutineScope(SupervisorJob() + this.coroutineContext),
    )
}
