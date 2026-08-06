package com.escapa2.radar.di

import android.content.Context
import androidx.room.Room
import com.escapa2.radar.data.device.DeviceTokenProvider
import com.escapa2.radar.data.device.NotificationPreferences
import com.escapa2.radar.data.device.SharedPreferencesDeviceTokenProvider
import com.escapa2.radar.data.device.SharedPreferencesNotificationPreferences
import com.escapa2.radar.data.local.Escapa2Database
import com.escapa2.radar.data.local.OpportunityDao
import com.escapa2.radar.data.remote.ApiClient
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.repository.AiRepository
import com.escapa2.radar.data.repository.AvailabilityRepository
import com.escapa2.radar.data.repository.CachedOpportunityRepository
import com.escapa2.radar.data.repository.DeviceRepository
import com.escapa2.radar.data.repository.FakeAiRepository
import com.escapa2.radar.data.repository.FakeAvailabilityRepository
import com.escapa2.radar.data.repository.FakeDeviceRepository
import com.escapa2.radar.data.repository.FakeOpportunityRepository
import com.escapa2.radar.data.repository.FakeProfileRepository
import com.escapa2.radar.data.repository.FakeSearchWatchRepository
import com.escapa2.radar.data.repository.FallbackAiRepository
import com.escapa2.radar.data.repository.FallbackAvailabilityRepository
import com.escapa2.radar.data.repository.FallbackDeviceRepository
import com.escapa2.radar.data.repository.FallbackOpportunityRepository
import com.escapa2.radar.data.repository.FallbackProfileRepository
import com.escapa2.radar.data.repository.FallbackSearchWatchRepository
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.data.repository.ProfileRepository
import com.escapa2.radar.data.repository.RemoteAiRepository
import com.escapa2.radar.data.repository.RemoteAvailabilityRepository
import com.escapa2.radar.data.repository.RemoteDeviceRepository
import com.escapa2.radar.data.repository.RemoteOpportunityRepository
import com.escapa2.radar.data.repository.RemoteProfileRepository
import com.escapa2.radar.data.repository.RemoteSearchWatchRepository
import com.escapa2.radar.data.repository.SearchWatchRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob

/**
 * Repository wiring: remote repositories are the primary source and fall back
 * to fake/local data when the backend is unreachable. Opportunity results are
 * cached into Room for offline access.
 */
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideEscapa2Api(): Escapa2Api = ApiClient.api

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): Escapa2Database =
        Room.databaseBuilder(
            context,
            Escapa2Database::class.java,
            "escapa2.db",
        ).build()

    @Provides
    fun provideOpportunityDao(database: Escapa2Database): OpportunityDao =
        database.opportunityDao()

    @Provides
    @Singleton
    fun provideOpportunityRepository(
        api: Escapa2Api,
        local: FakeOpportunityRepository,
        dao: OpportunityDao,
    ): OpportunityRepository {
        val fallbackSource = FallbackOpportunityRepository(
            RemoteOpportunityRepository(api),
            local,
        )
        return CachedOpportunityRepository(fallbackSource, dao)
    }

    @Provides
    @Singleton
    fun provideSearchWatchRepository(
        api: Escapa2Api,
        fallback: FakeSearchWatchRepository,
    ): SearchWatchRepository = FallbackSearchWatchRepository(RemoteSearchWatchRepository(api), fallback)

    @Provides
    @Singleton
    fun provideAvailabilityRepository(
        api: Escapa2Api,
        fallback: FakeAvailabilityRepository,
    ): AvailabilityRepository = FallbackAvailabilityRepository(RemoteAvailabilityRepository(api), fallback)

    @Provides
    @Singleton
    fun provideAiRepository(
        api: Escapa2Api,
        fallback: FakeAiRepository,
    ): AiRepository = FallbackAiRepository(RemoteAiRepository(api), fallback)

    @Provides
    @Singleton
    fun provideProfileRepository(
        api: Escapa2Api,
        fallback: FakeProfileRepository,
    ): ProfileRepository = FallbackProfileRepository(RemoteProfileRepository(api), fallback)

    @Provides
    @Singleton
    fun provideDeviceRepository(
        api: Escapa2Api,
        fallback: FakeDeviceRepository,
    ): DeviceRepository = FallbackDeviceRepository(RemoteDeviceRepository(api), fallback)

    @Provides
    @Singleton
    fun provideDeviceTokenProvider(@ApplicationContext context: Context): DeviceTokenProvider =
        SharedPreferencesDeviceTokenProvider(context)

    @Provides
    @Singleton
    fun provideNotificationPreferences(@ApplicationContext context: Context): NotificationPreferences =
        SharedPreferencesNotificationPreferences(context)

    @Provides
    @Singleton
    fun provideApplicationScope(): CoroutineScope =
        CoroutineScope(SupervisorJob() + Dispatchers.IO)
}
