package com.escapa2.radar.data.device

import com.google.firebase.messaging.FirebaseMessaging
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.filterNotNull

/**
 * Backs [DeviceTokenProvider] with the real Firebase Messaging token.
 *
 * The token is requested on creation; [refreshToken] is invoked by
 * [com.escapa2.radar.Escapa2MessagingService] whenever Firebase issues a new
 * token, which flows through [tokenUpdates] so the registrar re-registers the
 * device.
 */
@Singleton
class FcmDeviceTokenProvider @Inject constructor() : DeviceTokenProvider {

    private val _token = MutableStateFlow<String?>(null)

    override val token: String
        get() = _token.value.orEmpty()

    override val tokenUpdates: Flow<String> =
        _token.filterNotNull().distinctUntilChanged()

    init {
        FirebaseMessaging.getInstance().token
            .addOnSuccessListener { firebaseToken -> _token.value = firebaseToken }
    }

    fun refreshToken(firebaseToken: String) {
        _token.value = firebaseToken
    }
}
