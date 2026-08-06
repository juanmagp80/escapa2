package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.data.model.WatchRunResult

interface SearchWatchRepository {
    suspend fun getWatches(): List<SearchWatch>

    /**
     * Starts following a trip search. Returns the created watch.
     */
    suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch

    /**
     * Executes a watch once: refreshes run timestamps, records price snapshots
     * and evaluates the configured alert rules. Returns the alerts triggered.
     */
    suspend fun runWatch(id: String): WatchRunResult
}
