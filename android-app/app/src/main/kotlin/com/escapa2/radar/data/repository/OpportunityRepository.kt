package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.OpportunitySearchFilters

interface OpportunityRepository {
    suspend fun getOpportunities(): List<Opportunity>
    suspend fun getOpportunity(id: String): Opportunity?
    suspend fun search(filters: OpportunitySearchFilters): List<Opportunity>
}
