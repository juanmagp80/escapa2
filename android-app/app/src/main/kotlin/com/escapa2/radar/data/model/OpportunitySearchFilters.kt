package com.escapa2.radar.data.model

/**
 * Search criteria for the Explore screen.
 *
 * Nullable fields are optional filters that are not applied when null.
 */
data class OpportunitySearchFilters(
    val maxTotalCostEur: Double? = null,
    val transportMode: TransportMode? = null,
    val minUsefulHours: Double? = null,
    val destinationQuery: String? = null,
    val minNights: Int? = null,
    val maxNights: Int? = null,
)
