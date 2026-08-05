package com.escapa2.radar.data.remote

import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.remote.dto.AiSummaryDto
import com.escapa2.radar.data.remote.dto.AiSummaryRequestDto
import com.escapa2.radar.data.remote.dto.OpportunityDto
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Backend contract under the /api/v1 prefix.
 *
 * The base URL is a placeholder until the backend is deployed. The repository
 * layer falls back to fake data during development.
 */
interface Escapa2Api {

    @GET("opportunities")
    suspend fun getOpportunities(): List<OpportunityDto>

    @GET("opportunities/{id}")
    suspend fun getOpportunity(@Path("id") id: String): OpportunityDto

    @GET("opportunities")
    suspend fun searchOpportunities(
        @Query("max_total_cost_eur") maxTotalCostEur: Double? = null,
        @Query("transport_mode") transportMode: String? = null,
        @Query("min_useful_hours") minUsefulHours: Double? = null,
        @Query("destination") destination: String? = null,
    ): List<OpportunityDto>

    @POST("ai/opportunity-summary")
    suspend fun summarizeOpportunity(@Body body: AiSummaryRequestDto): AiSummaryDto
}
