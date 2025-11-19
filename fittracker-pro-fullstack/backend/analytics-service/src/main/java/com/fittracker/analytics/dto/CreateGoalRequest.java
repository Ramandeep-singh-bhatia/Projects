package com.fittracker.analytics.dto;

import com.fittracker.analytics.entity.UserGoal;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateGoalRequest {

    @NotNull(message = "User ID is required")
    private Long userId;

    @NotNull(message = "Goal type is required")
    private UserGoal.GoalType goalType;

    @NotNull(message = "Target value is required")
    @DecimalMin(value = "0.0", message = "Target value must be positive")
    private BigDecimal targetValue;

    @NotBlank(message = "Unit is required")
    @Size(max = 20, message = "Unit must not exceed 20 characters")
    private String unit;

    @NotNull(message = "Target date is required")
    @Future(message = "Target date must be in the future")
    private LocalDate targetDate;

    @Size(max = 500, message = "Description must not exceed 500 characters")
    private String description;
}
