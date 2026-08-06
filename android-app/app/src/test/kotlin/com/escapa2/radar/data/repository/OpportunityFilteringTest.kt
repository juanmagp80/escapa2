package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.TransportMode
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class OpportunityFilteringTest {

    private val car = sample("car", "Santiago de Compostela", TransportMode.CAR, 198.0, 34.0)
    private val flight = sample("flight", "Sevilla", TransportMode.FLIGHT, 246.0, 30.0)
    private val cheapFlight = sample("cheap", "Porto", TransportMode.FLIGHT, 214.0, 12.0)

    @Test
    fun noFiltersReturnsAll() {
        val result = filterOpportunities(
            listOf(car, flight, cheapFlight),
            OpportunitySearchFilters(),
        )

        assertEquals(3, result.size)
    }

    @Test
    fun budgetFiltersOutOverBudget() {
        val result = filterOpportunities(
            listOf(car, flight, cheapFlight),
            OpportunitySearchFilters(maxTotalCostEur = 220.0),
        )

        assertEquals(listOf("car", "cheap"), result.map { it.id })
    }

    @Test
    fun transportModeFiltersFlights() {
        val result = filterOpportunities(
            listOf(car, flight, cheapFlight),
            OpportunitySearchFilters(transportMode = TransportMode.FLIGHT),
        )

        assertEquals(2, result.size)
        assertTrue(result.all { it.transportMode == TransportMode.FLIGHT })
    }

    @Test
    fun eitherTransportMatchesAll() {
        val result = filterOpportunities(
            listOf(car, flight),
            OpportunitySearchFilters(transportMode = TransportMode.EITHER),
        )

        assertEquals(2, result.size)
    }

    @Test
    fun minUsefulHoursFiltersOutShortTrips() {
        val result = filterOpportunities(
            listOf(car, flight, cheapFlight),
            OpportunitySearchFilters(minUsefulHours = 20.0),
        )

        assertEquals(listOf("car", "flight"), result.map { it.id })
    }

    @Test
    fun destinationQueryIsCaseInsensitiveSubstring() {
        val result = filterOpportunities(
            listOf(car, flight, cheapFlight),
            OpportunitySearchFilters(destinationQuery = "porto"),
        )

        assertEquals(listOf("cheap"), result.map { it.id })
    }

    @Test
    fun combinedFiltersIntersect() {
        val result = filterOpportunities(
            listOf(car, flight, cheapFlight),
            OpportunitySearchFilters(
                maxTotalCostEur = 230.0,
                transportMode = TransportMode.FLIGHT,
            ),
        )

        assertEquals(listOf("cheap"), result.map { it.id })
    }

    @Test
    fun minNightsFiltersWeekendTrips() {
        val weekend = sample(
            id = "weekend",
            name = "Valencia",
            mode = TransportMode.CAR,
            total = 150.0,
            hours = 20.0,
        )
        val vacation = sample(
            id = "vacation",
            name = "Creta",
            mode = TransportMode.FLIGHT,
            total = 400.0,
            hours = 50.0,
        ).copy(
            startAt = "2026-08-14T08:00:00+02:00",
            endAt = "2026-08-19T20:00:00+02:00",
        )
        val result = filterOpportunities(
            listOf(weekend, vacation),
            OpportunitySearchFilters(minNights = 3),
        )

        assertEquals(listOf("vacation"), result.map { it.id })
    }

    @Test
    fun tripNightsComputesDaysBetweenDates() {
        val opportunity = sample("x", "Test", TransportMode.CAR, 100.0, 10.0)
        assertEquals(2, tripNights(opportunity))
    }

    @Test
    fun tripNightsReturnsZeroForInvalidDates() {
        val opportunity = sample("x", "Test", TransportMode.CAR, 100.0, 10.0)
            .copy(startAt = "not-a-date", endAt = "also-not-a-date")

        assertEquals(0, tripNights(opportunity))
    }

    @Test
    fun originFilterMatchesCaseInsensitive() {
        val madrid = sample("mad", "Valencia", TransportMode.CAR, 150.0, 20.0)
            .copy(originCity = "Madrid")
        val seville = sample("sev", "Cádiz", TransportMode.CAR, 120.0, 20.0)
            .copy(originCity = "Sevilla")
        val result = filterOpportunities(
            listOf(madrid, seville),
            OpportunitySearchFilters(originCity = "madrid"),
        )

        assertEquals(listOf("mad"), result.map { it.id })
    }

    @Test
    fun interestFilterMatchesListMembership() {
        val beach = sample("beach", "Almería", TransportMode.CAR, 150.0, 20.0)
            .copy(interests = listOf("playa"))
        val city = sample("city", "Valencia", TransportMode.CAR, 150.0, 20.0)
            .copy(interests = listOf("ciudad"))
        val result = filterOpportunities(
            listOf(beach, city),
            OpportunitySearchFilters(interest = "playa"),
        )

        assertEquals(listOf("beach"), result.map { it.id })
    }

    @Test
    fun startAfterFiltersTripsStartingTooEarly() {
        val early = sample("early", "Valencia", TransportMode.CAR, 150.0, 20.0)
        val late = sample("late", "Creta", TransportMode.FLIGHT, 400.0, 50.0)
            .copy(startAt = "2026-08-20T08:00:00+02:00")
        val result = filterOpportunities(
            listOf(early, late),
            OpportunitySearchFilters(startAfter = "2026-08-18T00:00:00Z"),
        )

        assertEquals(listOf("late"), result.map { it.id })
    }

    @Test
    fun endBeforeFiltersTripsEndingTooLate() {
        val early = sample("early", "Valencia", TransportMode.CAR, 150.0, 20.0)
        val late = sample("late", "Creta", TransportMode.FLIGHT, 400.0, 50.0)
            .copy(endAt = "2026-08-19T20:00:00+02:00")
        val result = filterOpportunities(
            listOf(early, late),
            OpportunitySearchFilters(endBefore = "2026-08-17T00:00:00Z"),
        )

        assertEquals(listOf("early"), result.map { it.id })
    }

    private fun sample(
        id: String,
        name: String,
        mode: TransportMode,
        total: Double,
        hours: Double,
    ) = Opportunity(
        id = id,
        destinationCode = id.uppercase(),
        destinationName = name,
        transportMode = mode,
        startAt = "2026-08-14T18:30:00+02:00",
        endAt = "2026-08-16T20:00:00+02:00",
        usefulHours = hours,
        totalCostEur = total,
        costPerPersonEur = total / 2,
        costPerNightEur = total / 2,
        costPerUsefulHourEur = total / hours,
        verifiedAt = "2026-08-05T12:00:00Z",
    )
}
