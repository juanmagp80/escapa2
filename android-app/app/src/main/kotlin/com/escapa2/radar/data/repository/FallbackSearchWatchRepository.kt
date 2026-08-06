package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.SearchWatch

/**
 * Tries the backend /watches endpoints and falls back to the local source on
 * connectivity or provider failures, so the Radar always has data to render.
 */
class FallbackSearchWatchRepository(
    private val remote: SearchWatchRepository,
    private val local: SearchWatchRepository,
) : SearchWatchRepository {

    override suspend fun getWatches(): List<SearchWatch> =
        try {
            remote.getWatches()
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.getWatches()
            } else {
                throw throwable
            }
        }

    override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch =
        try {
            remote.createWatch(name, initialPriceEur)
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.createWatch(name, initialPriceEur)
            } else {
                throw throwable
            }
        }
}
