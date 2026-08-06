package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AvailabilityWindow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Development-only source of availability windows, mirroring the backend mock.
 */
@Singleton
class FakeAvailabilityRepository @Inject constructor() : AvailabilityRepository {

    private val windows = listOf(
        AvailabilityWindow(
            id = "avail-1",
            startAt = "2026-08-14T18:00:00+02:00",
            endAt = "2026-08-16T22:00:00+02:00",
            kind = "WEEKEND",
            isFlexible = true,
        ),
        AvailabilityWindow(
            id = "avail-2",
            startAt = "2026-08-21T18:00:00+02:00",
            endAt = "2026-08-23T22:00:00+02:00",
            kind = "WEEKEND",
            isFlexible = false,
        ),
        AvailabilityWindow(
            id = "avail-3",
            startAt = "2026-09-28T00:00:00+02:00",
            endAt = "2026-10-04T23:59:00+02:00",
            kind = "VACATION",
            isFlexible = true,
        ),
    )

    override suspend fun getWindows(): List<AvailabilityWindow> = windows
}
