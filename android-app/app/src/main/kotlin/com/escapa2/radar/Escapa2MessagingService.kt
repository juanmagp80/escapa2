package com.escapa2.radar

import com.escapa2.radar.data.device.FcmDeviceTokenProvider
import com.google.firebase.messaging.FirebaseMessagingService
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Receives Firebase Messaging events. On token refresh it pushes the new token
 * into [FcmDeviceTokenProvider], which re-registers the device with the backend
 * when notifications are enabled.
 */
@AndroidEntryPoint
class Escapa2MessagingService : FirebaseMessagingService() {

    @Inject
    lateinit var tokenProvider: FcmDeviceTokenProvider

    override fun onNewToken(token: String) {
        tokenProvider.refreshToken(token)
    }
}
