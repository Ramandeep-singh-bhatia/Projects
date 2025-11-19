package com.fittracker.common.event;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserWeightUpdatedEvent implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long userId;
    private BigDecimal weightKg;
    private LocalDate recordedDate;
    private String eventId;
    private LocalDateTime eventTimestamp;

    public static UserWeightUpdatedEvent create(Long userId, BigDecimal weightKg, LocalDate recordedDate) {
        return UserWeightUpdatedEvent.builder()
                .userId(userId)
                .weightKg(weightKg)
                .recordedDate(recordedDate)
                .eventId(java.util.UUID.randomUUID().toString())
                .eventTimestamp(LocalDateTime.now())
                .build();
    }
}
