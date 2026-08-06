package com.escapa2.radar.data.repository

import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class FakeDeviceRepositoryTest {

    @Test
    fun registerIsIdempotentByToken() {
        val repository = FakeDeviceRepository()

        runBlocking {
            val first = repository.register("android-token-1")
            val second = repository.register("android-token-1")

            assertEquals(first.id, second.id)
            assertEquals(1, repository.registeredTokens.size)
            assertEquals("android-token-1", first.token)
            assertEquals("android", first.platform)
        }
    }

    @Test
    fun registerKeepsDifferentTokensSeparate() {
        val repository = FakeDeviceRepository()

        runBlocking {
            repository.register("android-token-a")
            repository.register("android-token-b")

            assertEquals(setOf("android-token-a", "android-token-b"), repository.registeredTokens)
        }
    }

    @Test
    fun unregisterRemovesToken() {
        val repository = FakeDeviceRepository()

        runBlocking {
            repository.register("android-token-2")
            assertTrue(repository.registeredTokens.contains("android-token-2"))

            repository.unregister("android-token-2")

            assertFalse(repository.registeredTokens.contains("android-token-2"))
        }
    }
}
