package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AvailabilityWindow

/**
 * Tries the backend availability endpoints and falls back to the local source
 * when the backend is unreachable.
 */
class FallbackAvailabilityRepository(
    private val remote: AvailabilityRepository,
    private val local: AvailabilityRepository,
) : AvailabilityRepository {

    override suspend fun getWindows(): List<AvailabilityWindow> =
        try {
            remote.getWindows()
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.getWindows()
            } else {
                throw throwable
            }
        }
}
