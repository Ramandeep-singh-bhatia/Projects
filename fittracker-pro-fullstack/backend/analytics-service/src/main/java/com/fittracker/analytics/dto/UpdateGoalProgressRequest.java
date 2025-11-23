package com.fittracker.analytics.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateGoalProgressRequest {

    @NotNull(message = "Current value is required")
    @DecimalMin(value = "0.0", message = "Current value must be positive")
    private BigDecimal currentValue;

    @Size(max = 500, message = "Notes must not exceed 500 characters")
    private String notes;
}
