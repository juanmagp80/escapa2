package com.escapa2.radar.data.device

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Persists a stable per-install device token in SharedPreferences and reuses it
 * across launches.
 */
@Singleton
class SharedPreferencesDeviceTokenProvider @Inject constructor(
    @ApplicationContext context: Context,
) : DeviceTokenProvider {

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    override val token: String = prefs.getString(KEY_TOKEN, null) ?: generateAndPersist()

    private fun generateAndPersist(): String {
        val newToken = "android-${UUID.randomUUID()}"
        prefs.edit().putString(KEY_TOKEN, newToken).apply()
        return newToken
    }

    private companion object {
        const val PREFS_NAME = "escapa2_device"
        const val KEY_TOKEN = "device_token"
    }
}
