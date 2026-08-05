package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.TravelProfile

/**
 * Tries the backend profile endpoints and falls back to the local in-memory
 * copy when the backend is unreachable, keeping the profile screen usable
 * during development and offline.
 */
class FallbackProfileRepository(
    private val remote: ProfileRepository,
    private val local: ProfileRepository,
) : ProfileRepository {

    override suspend fun getProfile(): TravelProfile =
        try {
            remote.getProfile()
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.getProfile()
            } else {
                throw throwable
            }
        }

    override suspend fun saveProfile(profile: TravelProfile): TravelProfile =
        try {
            remote.saveProfile(profile)
        } catch (throwable: Throwable) {
            if (NetworkFallback.shouldFallBack(throwable)) {
                local.saveProfile(profile)
            } else {
                throw throwable
            }
        }
}
