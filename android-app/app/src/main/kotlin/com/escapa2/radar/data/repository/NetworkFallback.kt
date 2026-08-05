package com.escapa2.radar.data.repository

import java.io.IOException
import retrofit2.HttpException

/**
 * Shared decision for repository fallbacks: only fall back on connectivity
 * errors or provider failures (5xx), never on client errors (4xx) so that
 * invalid requests surface instead of being silently masked by fake data.
 */
internal object NetworkFallback {

    fun shouldFallBack(throwable: Throwable): Boolean =
        throwable is IOException ||
            (throwable is HttpException && throwable.code() >= 500)
}
