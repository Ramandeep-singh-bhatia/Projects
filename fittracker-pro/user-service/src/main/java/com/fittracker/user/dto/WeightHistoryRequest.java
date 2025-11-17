package com.fittracker.user.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
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
public class WeightHistoryRequest {

    @NotNull(message = "Weight is required")
    @DecimalMin(value = "0.0", inclusive = false, message = "Weight must be greater than 0")
    private BigDecimal weightKg;

    @DecimalMin(value = "0.0", message = "Body fat percentage must be non-negative")
    private BigDecimal bodyFatPercentage;

    @DecimalMin(value = "0.0", message = "Muscle mass must be non-negative")
    private BigDecimal muscleMassKg;

    private String notes;

    private LocalDateTime recordedAt;
}
