package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.SearchWatch
import java.time.Instant
import java.time.temporal.ChronoUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Development-only source of watched trips.
 *
 * Values are orientative placeholders until the Radar diario (Fase 4) stores
 * real runs, snapshots and alert evaluations. New watches created from the
 * opportunity detail are kept in memory for the session.
 */
@Singleton
class FakeSearchWatchRepository @Inject constructor() : SearchWatchRepository {

    private val watches = mutableListOf(
        SearchWatch(
            id = "watch-porto",
            name = "Porto en avión",
            status = "ACTIVE",
            lastRunAt = "2026-08-05T12:00:00Z",
            nextRunAt = "2026-08-06T12:00:00Z",
            changeSinceYesterdayEur = -16.0,
            minRecordedEur = 312.0,
            alertRules = listOf("Nuevo mínimo histórico", "Viaje por debajo de 350 EUR"),
            priceHistory = listOf(328.0, 312.0),
        ),
        SearchWatch(
            id = "watch-galicia",
            name = "Galicia en coche",
            status = "ACTIVE",
            lastRunAt = "2026-08-05T12:00:00Z",
            nextRunAt = "2026-08-06T12:00:00Z",
            changeSinceYesterdayEur = 0.0,
            minRecordedEur = 198.0,
            alertRules = listOf("Bajada superior a 10%"),
            priceHistory = listOf(212.0, 198.0),
        ),
    )

    override suspend fun getWatches(): List<SearchWatch> = watches.toList()

    override suspend fun createWatch(name: String, initialPriceEur: Double): SearchWatch {
        val now = Instant.now()
        val nextRun = now.plus(1, ChronoUnit.DAYS)
        val watch = SearchWatch(
            id = "watch-${watches.size + 1}",
            name = name,
            status = "ACTIVE",
            lastRunAt = now.toString(),
            nextRunAt = nextRun.toString(),
            changeSinceYesterdayEur = 0.0,
            minRecordedEur = initialPriceEur,
            alertRules = listOf("Nuevo mínimo histórico"),
            priceHistory = listOf(initialPriceEur),
        )
        watches.add(watch)
        return watch
    }
}
