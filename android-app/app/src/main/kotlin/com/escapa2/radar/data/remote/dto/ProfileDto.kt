package com.escapa2.radar.data.remote.dto

import com.escapa2.radar.data.model.AirportPreference
import com.escapa2.radar.data.model.TransportMode
import com.escapa2.radar.data.model.TravelProfile
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ProfileDto(
    val id: String,
    @SerialName("origin_city") val originCity: String,
    val currency: String,
    @SerialName("default_budget_eur") val defaultBudgetEur: Double? = null,
    @SerialName("max_drive_minutes") val maxDriveMinutes: Int? = null,
    @SerialName("preferred_transport") val preferredTransport: String = "EITHER",
    val interests: List<String> = emptyList(),
    @SerialName("avoid_preferences") val avoidPreferences: List<String> = emptyList(),
)

@Serializable
data class ProfileUpdateDto(
    @SerialName("origin_city") val originCity: String,
    val currency: String,
    @SerialName("default_budget_eur") val defaultBudgetEur: Double? = null,
    @SerialName("max_drive_minutes") val maxDriveMinutes: Int? = null,
    @SerialName("preferred_transport") val preferredTransport: String,
    val interests: List<String> = emptyList(),
    @SerialName("avoid_preferences") val avoidPreferences: List<String> = emptyList(),
)

@Serializable
data class AirportPreferenceDto(
    @SerialName("iata_code") val iataCode: String,
    val enabled: Boolean = true,
    @SerialName("transfer_cost_eur") val transferCostEur: Double? = null,
    @SerialName("transfer_minutes") val transferMinutes: Int? = null,
)

fun ProfileDto.toDomain(): TravelProfile = TravelProfile(
    id = id,
    originCity = originCity,
    currency = currency,
    defaultBudgetEur = defaultBudgetEur,
    maxDriveMinutes = maxDriveMinutes,
    preferredTransport = runCatching { TransportMode.valueOf(preferredTransport) }
        .getOrDefault(TransportMode.EITHER),
    interests = interests,
    avoidPreferences = avoidPreferences,
    airports = emptyList(),
)

fun TravelProfile.toUpdateDto(): ProfileUpdateDto = ProfileUpdateDto(
    originCity = originCity,
    currency = currency,
    defaultBudgetEur = defaultBudgetEur,
    maxDriveMinutes = maxDriveMinutes,
    preferredTransport = preferredTransport.name,
    interests = interests,
    avoidPreferences = avoidPreferences,
)

fun AirportPreferenceDto.toDomain(): AirportPreference = AirportPreference(
    id = iataCode,
    iataCode = iataCode,
    enabled = enabled,
    transferCostEur = transferCostEur,
    transferMinutes = transferMinutes,
)

fun AirportPreference.toInputDto(): AirportPreferenceDto = AirportPreferenceDto(
    iataCode = iataCode,
    enabled = enabled,
    transferCostEur = transferCostEur,
    transferMinutes = transferMinutes,
)
