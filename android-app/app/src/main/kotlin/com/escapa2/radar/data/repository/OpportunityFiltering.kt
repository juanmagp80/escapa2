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

        val originMatches = filters.originCity == null ||
            opportunity.originCity.equals(filters.originCity, ignoreCase = true)

        val interestMatches = filters.interest == null ||
            filters.interest in opportunity.interests

        val startsAfter = filters.startAfter == null ||
            after(opportunity.startAt, filters.startAfter)

        val endsBefore = filters.endBefore == null ||
            before(opportunity.endAt, filters.endBefore)

        val nights = tripNights(opportunity)
        val withinDuration = (filters.minNights == null || nights >= filters.minNights) &&
            (filters.maxNights == null || nights <= filters.maxNights)

        withinBudget && transportMatches && enoughUsefulHours &&
            destinationMatches && originMatches && interestMatches &&
            startsAfter && endsBefore && withinDuration
    }
}

private fun after(candidate: String, reference: String): Boolean {
    val parsed = runCatching { Instant.parse(candidate) }.getOrNull() ?: return false
    val ref = runCatching { Instant.parse(reference) }.getOrNull() ?: return true
    return !parsed.isBefore(ref)
}

private fun before(candidate: String, reference: String): Boolean {
    val parsed = runCatching { Instant.parse(candidate) }.getOrNull() ?: return false
    val ref = runCatching { Instant.parse(reference) }.getOrNull() ?: return true
    return !parsed.isAfter(ref)
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
