package com.escapa2.radar.data.device

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Stores the push-notification preference in SharedPreferences.
 */
@Singleton
class SharedPreferencesNotificationPreferences @Inject constructor(
    @ApplicationContext context: Context,
) : NotificationPreferences {

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    override var notificationsEnabled: Boolean
        get() = prefs.getBoolean(KEY_ENABLED, false)
        set(value) {
            prefs.edit().putBoolean(KEY_ENABLED, value).apply()
        }

    private companion object {
        const val PREFS_NAME = "escapa2_device"
        const val KEY_ENABLED = "notifications_enabled"
    }
}
