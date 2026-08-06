package com.escapa2.radar.data.device

import com.escapa2.radar.data.repository.DeviceRepository
import com.escapa2.radar.data.repository.FakeDeviceRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.consumeAsFlow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class DeviceRegistrarTest {

    private class FakeTokenProvider(override val token: String) : DeviceTokenProvider {
        override val tokenUpdates: Flow<String> = flowOf(token)
    }

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

    @Test
    fun tokenRefreshRegistersNewTokenAndUnregistersPrevious() = runTest {
        val repository = FakeDeviceRepository()
        val channel = Channel<String>(Channel.BUFFERED)
        val registrar = DeviceRegistrar(
            repository = repository,
            tokenProvider = object : DeviceTokenProvider {
                override val token: String
                    get() = "android-token-old"
                override val tokenUpdates: Flow<String> = channel.consumeAsFlow()
            },
            preferences = FakeNotificationPreferences(),
            scope = CoroutineScope(SupervisorJob() + this.coroutineContext),
        )

        channel.send("android-token-old")
        registrar.setNotificationsEnabled(true)
        advanceUntilIdle()
        assertEquals(setOf("android-token-old"), repository.registeredTokens)

        channel.send("android-token-new")
        advanceUntilIdle()

        channel.close()
        assertEquals(setOf("android-token-new"), repository.registeredTokens)
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
