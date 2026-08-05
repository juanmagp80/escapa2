package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters

/**
 * Tries the remote backend and falls back to the local source on connectivity
 * or provider failures, so the UI always has data to render (fake during
 * development, cached data in production).
 */
class FallbackOpportunityRepository(
    private val remote: OpportunityRepository,
    private val local: OpportunityRepository,
) : OpportunityRepository {

    override suspend fun getOpportunities(): List<Opportunity> =
        try {
            remote.getOpportunities()
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.getOpportunities()
            } else {
                throw throwable
            }
        }

    override suspend fun getOpportunity(id: String): Opportunity? =
        try {
            remote.getOpportunity(id)
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.getOpportunity(id)
            } else {
                throw throwable
            }
        }

    override suspend fun search(filters: OpportunitySearchFilters): List<Opportunity> =
        try {
            remote.search(filters)
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.search(filters)
            } else {
                throw throwable
            }
        }
}
