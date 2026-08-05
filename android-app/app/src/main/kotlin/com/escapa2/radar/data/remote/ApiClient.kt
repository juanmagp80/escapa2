package com.escapa2.radar.data.remote

import com.escapa2.radar.BuildConfig
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {

    /**
     * Backend base URL under the /api/v1 prefix.
     *
     * The default points to the deployed backend; override it with the Gradle
     * property `escapa2ApiBaseUrl` (e.g. `-Pescapa2ApiBaseUrl=http://...`).
     * The repository layer falls back to fake data when the backend is not
     * reachable.
     */
    val BASE_URL: String = BuildConfig.API_BASE_URL

    private val json: Json = Json {
        ignoreUnknownKeys = true
        explicitNulls = false
    }

    private val okHttpClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .addInterceptor(
            HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BASIC
            }
        )
        .build()

    private val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()

    val api: Escapa2Api by lazy { retrofit.create(Escapa2Api::class.java) }
}
