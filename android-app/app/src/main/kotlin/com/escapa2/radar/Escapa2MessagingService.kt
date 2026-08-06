package com.escapa2.radar

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.net.Uri
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.escapa2.radar.data.device.FcmDeviceTokenProvider
import com.escapa2.radar.navigation.DeepLinks
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Receives Firebase Messaging events.
 *
 * On token refresh it pushes the new token into [FcmDeviceTokenProvider], which
 * re-registers the device with the backend when notifications are enabled.
 *
 * Foreground messages are rendered as a system notification here, because FCM
 * only shows notifications automatically when the app is in the background. The
 * tap opens the deep link provided by the backend (e.g. the radar screen).
 */
@AndroidEntryPoint
class Escapa2MessagingService : FirebaseMessagingService() {

    @Inject
    lateinit var tokenProvider: FcmDeviceTokenProvider

    override fun onNewToken(token: String) {
        tokenProvider.refreshToken(token)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val notification = message.notification
        val title = notification?.title ?: getString(R.string.app_name)
        val body = notification?.body ?: message.data[MESSAGE_KEY_BODY] ?: ""
        if (body.isBlank()) return
        val deepLink = message.data[KEY_DEEP_LINK] ?: DeepLinks.RADAR
        showNotification(title, body, deepLink)
    }

    private fun showNotification(title: String, body: String, deepLink: String) {
        val manager = NotificationManagerCompat.from(this)
        if (!manager.areNotificationsEnabled()) return
        manager.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ID,
                getString(R.string.notification_channel_radar),
                NotificationManager.IMPORTANCE_DEFAULT,
            )
        )
        val openLink = Intent(Intent.ACTION_VIEW, Uri.parse(deepLink)).apply {
            flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        val pendingIntent = PendingIntent.getActivity(
            this,
            NOTIFICATION_ID,
            openLink,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val rendered = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()
        manager.notify(NOTIFICATION_ID, rendered)
    }

    private companion object {
        const val CHANNEL_ID = "radar_alerts"
        const val NOTIFICATION_ID = 1001
        const val KEY_DEEP_LINK = "deep_link"
        const val MESSAGE_KEY_BODY = "body"
    }
}
