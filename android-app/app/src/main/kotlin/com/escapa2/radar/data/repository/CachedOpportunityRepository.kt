package com.escapa2.radar.data.repository

import com.escapa2.radar.data.local.OpportunityDao
import com.escapa2.radar.data.local.toDomain
import com.escapa2.radar.data.local.toEntity
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.model.PriceSnapshot

/**
 * Repository that caches remote/fake results into Room.
 *
 * On network failure it falls back to the cached copy so saved trips remain
 * readable offline. The cache is a copy, never the source of truth.
 */
class CachedOpportunityRepository(
    private val source: OpportunityRepository,
    private val dao: OpportunityDao,
) : OpportunityRepository {

    override suspend fun getOpportunities(): List<Opportunity> =
        getOrFallback { source.getOpportunities() }

    override suspend fun getOpportunity(id: String): Opportunity? =
        try {
            source.getOpportunity(id)?.also { cached -> dao.upsert(cached.toEntity()) }
        } catch (e: Exception) {
            dao.getById(id)?.toDomain()
        }

    override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
        getOrFallback { source.search(filters) }

    override suspend fun getPriceHistory(id: String): List<PriceSnapshot> =
        try {
            source.getPriceHistory(id)
        } catch (e: Exception) {
            emptyList()
        }

    private suspend fun getOrFallback(block: suspend () -> List<Opportunity>): List<Opportunity> {
        return try {
            block().also { results -> dao.upsertAll(results.map { it.toEntity() }) }
        } catch (e: Exception) {
            dao.getAll().map { it.toDomain() }
        }
    }
}
