package com.escapa2.radar.data.model

/**
 * Couple travel preferences used to find getaways.
 */
data class TravelProfile(
    val id: String,
    val originCity: String,
    val currency: String,
    val defaultBudgetEur: Double?,
    val maxDriveMinutes: Int?,
    val preferredTransport: TransportMode,
    val interests: List<String>,
    val avoidPreferences: List<String>,
    val airports: List<AirportPreference>,
)

/**
 * An accepted departure airport with its ground transfer data.
 */
data class AirportPreference(
    val id: String,
    val iataCode: String,
    val enabled: Boolean,
    val transferCostEur: Double?,
    val transferMinutes: Int?,
)
