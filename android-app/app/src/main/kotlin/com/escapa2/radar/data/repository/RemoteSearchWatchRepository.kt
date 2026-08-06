package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.remote.dto.SearchWatchCreateDto
import com.escapa2.radar.data.remote.dto.defaultAlertRules
import com.escapa2.radar.data.remote.dto.initialPriceCriteria
import com.escapa2.radar.data.remote.dto.toDomain

/**
 * Repository backed by the backend /watches endpoints.
 */
class RemoteSearchWatchRepository(
    private val api: Escapa2Api,
) : SearchWatchRepository {

    override suspend fun getWatches(): List<SearchWatch> =
        api.getWatches().map { it.toDomain() }

    override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch =
        api.createWatch(
            SearchWatchCreateDto(
                name = name,
                criteria = initialPriceCriteria(initialPriceEur),
                alertRules = defaultAlertRules(),
            ),
        ).toDomain()
}
