package com.escapa2.radar.navigation

/**
 * Deep link URIs used by push notifications. The scheme/host must match the
 * intent-filter declared in [AndroidManifest.xml] and the destinations in
 * [Escapa2NavHost].
 */
object DeepLinks {
    const val SCHEME = "escapa2"
    const val RADAR = "$SCHEME://radar"
}
