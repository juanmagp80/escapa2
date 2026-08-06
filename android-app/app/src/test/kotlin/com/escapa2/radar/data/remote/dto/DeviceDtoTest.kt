package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.DeviceRegistration
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Test

class DeviceDtoTest {

    private val json = Json { ignoreUnknownKeys = true }

    @Test
    fun toDomainMapsSnakeCaseFields() {
        val dto = DeviceRegistrationDto(
            id = "device-1",
            userId = "dev-user",
            token = "android-token-123",
            platform = "android",
        )

        val domain = dto.toDomain()

        assertEquals("device-1", domain.id)
        assertEquals("dev-user", domain.userId)
        assertEquals("android-token-123", domain.token)
        assertEquals("android", domain.platform)
    }

    @Test
    fun decodesDeviceResponseFromSnakeCaseJson() {
        val dto = json.decodeFromString<DeviceRegistrationDto>(
            """
            {
              "id": "device-2",
              "user_id": "dev-user",
              "token": "android-token-456",
              "platform": "android"
            }
            """.trimIndent(),
        )

        assertEquals("dev-user", dto.userId)
        assertEquals("android-token-456", dto.token)
    }

    @Test
    fun requestDtoSerializesTokenAndSkipsDefaultPlatform() {
        val body = RegisterDeviceRequestDto(token = "android-token-789")

        val serialized = json.encodeToString(RegisterDeviceRequestDto.serializer(), body)

        assertEquals(
            """{"token":"android-token-789"}""",
            serialized,
        )
    }
}
