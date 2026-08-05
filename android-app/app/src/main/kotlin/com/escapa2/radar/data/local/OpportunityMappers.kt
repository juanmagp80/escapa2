package com.escapa2.radar.data.local

import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.TransportMode

fun OpportunityEntity.toDomain(): Opportunity = Opportunity(
    id = id,
    destinationCode = destinationCode,
    destinationName = destinationName,
    transportMode = runCatching { TransportMode.valueOf(transportMode) }
        .getOrDefault(TransportMode.EITHER),
    startAt = startAt,
    endAt = endAt,
    usefulHours = usefulHours,
    totalCostEur = totalCostEur,
    costPerPersonEur = costPerPersonEur,
    costPerNightEur = costPerNightEur,
    costPerUsefulHourEur = costPerUsefulHourEur,
    verifiedAt = verifiedAt,
)

fun Opportunity.toEntity(): OpportunityEntity = OpportunityEntity(
    id = id,
    destinationCode = destinationCode,
    destinationName = destinationName,
    transportMode = transportMode.name,
    startAt = startAt,
    endAt = endAt,
    usefulHours = usefulHours,
    totalCostEur = totalCostEur,
    costPerPersonEur = costPerPersonEur,
    costPerNightEur = costPerNightEur,
    costPerUsefulHourEur = costPerUsefulHourEur,
    verifiedAt = verifiedAt,
)
