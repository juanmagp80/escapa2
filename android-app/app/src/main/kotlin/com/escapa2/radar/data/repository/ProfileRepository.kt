package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.TravelProfile

/**
 * Contract for the couple travel profile used by the UI.
 */
interface ProfileRepository {

    suspend fun getProfile(): TravelProfile

    suspend fun saveProfile(profile: TravelProfile): TravelProfile
}
