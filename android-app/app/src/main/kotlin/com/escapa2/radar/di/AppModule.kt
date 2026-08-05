package com.escapa2.radar.di

import android.content.Context
import androidx.room.Room
import com.escapa2.radar.data.local.Escapa2Database
import com.escapa2.radar.data.local.OpportunityDao
import com.escapa2.radar.data.remote.ApiClient
import com.escapa2.radar.data.remote.Escapa2Api
import com.escapa2.radar.data.repository.AiRepository
import com.escapa2.radar.data.repository.CachedOpportunityRepository
import com.escapa2.radar.data.repository.FakeAiRepository
import com.escapa2.radar.data.repository.FakeOpportunityRepository
import com.escapa2.radar.data.repository.FakeProfileRepository
import com.escapa2.radar.data.repository.FakeSearchWatchRepository
import com.escapa2.radar.data.repository.OpportunityRepository
import com.escapa2.radar.data.repository.ProfileRepository
import com.escapa2.radar.data.repository.SearchWatchRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Development wiring: the fake repository is the default until the backend
 * deployment is available. Results are cached into Room for offline access.
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
        source: FakeOpportunityRepository,
        dao: OpportunityDao,
    ): OpportunityRepository = CachedOpportunityRepository(source, dao)

    @Provides
    @Singleton
    fun provideSearchWatchRepository(source: FakeSearchWatchRepository): SearchWatchRepository =
        source

    @Provides
    @Singleton
    fun provideAiRepository(source: FakeAiRepository): AiRepository = source

    @Provides
    @Singleton
    fun provideProfileRepository(source: FakeProfileRepository): ProfileRepository = source
}
