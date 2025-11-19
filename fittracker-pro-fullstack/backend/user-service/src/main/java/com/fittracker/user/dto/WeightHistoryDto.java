package com.fittracker.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WeightHistoryDto {

    private Long id;
    private Long userId;
    private BigDecimal weightKg;
    private BigDecimal bodyFatPercentage;
    private BigDecimal muscleMassKg;
    private String notes;
    private LocalDateTime recordedAt;
}
