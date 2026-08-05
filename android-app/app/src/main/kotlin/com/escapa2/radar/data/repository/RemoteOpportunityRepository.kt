package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.remote.dto.toDomain

/**
 * Repository backed by the Escapa2 backend.
 *
 * Prices are considered stale if [maxStaleHours] is exceeded.
 */
class RemoteOpportunityRepository(
    private val api: Escapa2Api,
    private val maxStaleHours: Int = 24,
) : OpportunityRepository {

    override suspend fun getOpportunities(): List<Opportunity> =
        api.getOpportunities().map { it.toDomain() }

    override suspend fun getOpportunity(id: String): Opportunity? =
        api.getOpportunity(id).toDomain()

    override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
        api.searchOpportunities(
            maxTotalCostEur = filters.maxTotalCostEur,
            transportMode = filters.transportMode?.name,
            minUsefulHours = filters.minUsefulHours,
            destination = filters.destinationQuery,
        ).map { it.toDomain() }
}
