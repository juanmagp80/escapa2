package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.TransportMode
import java.time.Duration
import java.time.Instant

/**
 * Pure filtering logic for travel opportunities.
 *
 * A filter is only applied when its value is non-null.
 */
fun filterOpportunities(
    opportunities: List<Opportunity>,
    filters: OpportunitySearchFilters,
): List<Opportunity> {
    return opportunities.filter { opportunity ->
        val withinBudget = filters.maxTotalCostEur == null ||
            opportunity.totalCostEur <= filters.maxTotalCostEur

        val transportMatches = filters.transportMode == null ||
            filters.transportMode == TransportMode.EITHER ||
            opportunity.transportMode == filters.transportMode

        val enoughUsefulHours = filters.minUsefulHours == null ||
            opportunity.usefulHours >= filters.minUsefulHours

        val destinationMatches = filters.destinationQuery == null ||
            opportunity.destinationName.contains(filters.destinationQuery, ignoreCase = true)

        val nights = tripNights(opportunity)
        val withinDuration = (filters.minNights == null || nights >= filters.minNights) &&
            (filters.maxNights == null || nights <= filters.maxNights)

        withinBudget && transportMatches && enoughUsefulHours &&
            destinationMatches && withinDuration
    }
}

/**
 * Nights between start and end. Returns 0 when dates cannot be parsed.
 */
fun tripNights(opportunity: Opportunity): Int {
    val start = runCatching { Instant.parse(opportunity.startAt) }.getOrNull()
        ?: return 0
    val end = runCatching { Instant.parse(opportunity.endAt) }.getOrNull()
        ?: return 0
    return Duration.between(start, end).toDays().toInt().coerceAtLeast(0)
}
