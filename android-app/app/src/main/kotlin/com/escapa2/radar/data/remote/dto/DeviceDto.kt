package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.DeviceRegistration
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class RegisterDeviceRequestDto(
    val token: String,
    val platform: String = "android",
)

@Serializable
data class DeviceRegistrationDto(
    val id: String,
    @SerialName("user_id") val userId: String,
    val token: String,
    val platform: String,
)

fun DeviceRegistrationDto.toDomain(): DeviceRegistration = DeviceRegistration(
    id = id,
    userId = userId,
    token = token,
    platform = platform,
)
