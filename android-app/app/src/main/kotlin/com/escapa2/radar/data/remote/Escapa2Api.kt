package com.escapa2.radar.data.remote

import com.escapa2.radar.data.model.OpportunitySearchFilters
import com.escapa2.radar.data.remote.dto.AiSummaryDto
import com.escapa2.radar.data.remote.dto.AiSummaryRequestDto
import com.escapa2.radar.data.remote.dto.AirportPreferenceDto
import com.escapa2.radar.data.remote.dto.AvailabilityWindowDto
import com.escapa2.radar.data.remote.dto.OpportunityDto
import com.escapa2.radar.data.remote.dto.ProfileDto
import com.escapa2.radar.data.remote.dto.ProfileUpdateDto
import com.escapa2.radar.data.remote.dto.SearchWatchCreateDto
import com.escapa2.radar.data.remote.dto.SearchWatchDto
import com.escapa2.radar.data.remote.dto.WatchRunResultDto
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
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
        @Query("origin") origin: String? = null,
        @Query("interest") interest: String? = null,
        @Query("start_after") startAfter: String? = null,
        @Query("end_before") endBefore: String? = null,
        @Query("sort") sort: String? = null,
    ): List<OpportunityDto>

    @POST("ai/opportunity-summary")
    suspend fun summarizeOpportunity(@Body body: AiSummaryRequestDto): AiSummaryDto

    @GET("profile")
    suspend fun getProfile(): ProfileDto

    @PUT("profile")
    suspend fun updateProfile(@Body body: ProfileUpdateDto): ProfileDto

    @GET("profile/airports")
    suspend fun getAirports(): List<AirportPreferenceDto>

    @PUT("profile/airports")
    suspend fun replaceAirports(@Body body: List<AirportPreferenceDto>): List<AirportPreferenceDto>

    @GET("watches")
    suspend fun getWatches(): List<SearchWatchDto>

    @POST("watches")
    suspend fun createWatch(@Body body: SearchWatchCreateDto): SearchWatchDto

    @POST("watches/{id}/run")
    suspend fun runWatch(@Path("id") id: String): WatchRunResultDto

    @GET("availability")
    suspend fun getAvailabilityWindows(): List<AvailabilityWindowDto>
}
