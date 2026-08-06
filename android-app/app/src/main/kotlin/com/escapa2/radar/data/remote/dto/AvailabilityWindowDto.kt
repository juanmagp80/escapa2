package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.AvailabilityWindow
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AvailabilityWindowDto(
    val id: String,
    @SerialName("start_at") val startAt: String,
    @SerialName("end_at") val endAt: String,
    val kind: String = "WEEKEND",
    @SerialName("is_flexible") val isFlexible: Boolean = false,
)

fun AvailabilityWindowDto.toDomain(): AvailabilityWindow = AvailabilityWindow(
    id = id,
    startAt = startAt,
    endAt = endAt,
    kind = kind,
    isFlexible = isFlexible,
)
