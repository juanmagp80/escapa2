package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.SearchWatch

interface SearchWatchRepository {
    suspend fun getWatches(): List<SearchWatch>

    /**
     * Starts following a trip search. Returns the created watch.
     */
    suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch
}
