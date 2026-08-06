package com.escapa2.radar.data.model

/**
 * Normalized travel opportunity used by the UI.
 *
 * Prices are orientative and always carry a [verifiedAt] timestamp.
 */
data class Opportunity(
    val id: String,
    val destinationCode: String,
    val destinationName: String,
    val transportMode: TransportMode,
    val startAt: String,
    val endAt: String,
    val usefulHours: Double,
    val totalCostEur: Double,
    val costPerPersonEur: Double,
    val costPerNightEur: Double,
    val costPerUsefulHourEur: Double,
    val verifiedAt: String,
    val previousTotalCostEur: Double? = null,
    val valueScore: Double? = null,
    val originCity: String? = null,
    val interests: List<String> = emptyList(),
    val flightCostEur: Double? = null,
    val hotelCostEur: Double? = null,
    val routeCostEur: Double? = null,
    val bookingUrl: String? = null,
)
