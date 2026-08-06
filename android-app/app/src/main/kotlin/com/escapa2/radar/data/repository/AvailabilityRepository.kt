package com.escapa2.radar.data.repository

import com.escapa2.radar.data.model.AvailabilityWindow

/**
 * Contract for the couple's free travel dates.
 */
interface AvailabilityRepository {
    suspend fun getWindows(): List<AvailabilityWindow>
}
