package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.TransportMode
import javax.inject.Inject

/**
 * Development-only source of opportunities.
 *
 * Demonstrates total cost, per person, per night, per useful hour, the price
 * difference versus a previous snapshot and the verification timestamp.
 */
class FakeOpportunityRepository @Inject constructor() : OpportunityRepository {

    override suspend fun getOpportunities(): List<Opportunity> = opportunities

    override suspend fun getOpportunity(id: String): Opportunity? =
        opportunities.firstOrNull { it.id == id }

    override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
        filterOpportunities(opportunities, filters)

    private companion object {
        val opportunities: List<Opportunity> = listOf(
        Opportunity(
            id = "opp-coche-galicia",
            destinationCode = "GAL",
            destinationName = "Santiago de Compostela",
            transportMode = TransportMode.CAR,
            startAt = "2026-08-14T18:30:00+02:00",
            endAt = "2026-08-16T20:00:00+02:00",
            usefulHours = 34.0,
            totalCostEur = 198.0,
            costPerPersonEur = 99.0,
            costPerNightEur = 99.0,
            costPerUsefulHourEur = 5.82,
            verifiedAt = "2026-08-05T12:00:00Z",
            previousTotalCostEur = 212.0,
            valueScore = 100.0,
        ),
        Opportunity(
            id = "opp-avion-andalucia",
            destinationCode = "SVQ",
            destinationName = "Sevilla",
            transportMode = TransportMode.FLIGHT,
            startAt = "2026-08-14T19:45:00+02:00",
            endAt = "2026-08-16T21:10:00+02:00",
            usefulHours = 30.0,
            totalCostEur = 246.0,
            costPerPersonEur = 123.0,
            costPerNightEur = 123.0,
            costPerUsefulHourEur = 8.20,
            verifiedAt = "2026-08-05T12:00:00Z",
            previousTotalCostEur = 270.0,
            valueScore = 89.4,
        ),
        Opportunity(
            id = "opp-avion-porto",
            destinationCode = "OPO",
            destinationName = "Porto",
            transportMode = TransportMode.FLIGHT,
            startAt = "2026-08-21T08:10:00+02:00",
            endAt = "2026-08-23T19:30:00+02:00",
            usefulHours = 40.0,
            totalCostEur = 312.0,
            costPerPersonEur = 156.0,
            costPerNightEur = 156.0,
            costPerUsefulHourEur = 7.80,
            verifiedAt = "2026-08-05T12:00:00Z",
            previousTotalCostEur = 328.0,
            valueScore = 75.5,
        ),
        Opportunity(
            id = "opp-avion-porto-barata",
            destinationCode = "OPO",
            destinationName = "Porto (horario ajustado)",
            transportMode = TransportMode.FLIGHT,
            startAt = "2026-08-21T22:00:00+02:00",
            endAt = "2026-08-23T06:30:00+02:00",
            usefulHours = 12.0,
            totalCostEur = 214.0,
            costPerPersonEur = 107.0,
            costPerNightEur = 107.0,
            costPerUsefulHourEur = 17.83,
            verifiedAt = "2026-08-05T12:00:00Z",
            previousTotalCostEur = 226.0,
            valueScore = 64.8,
        ),
    )
    }
}
