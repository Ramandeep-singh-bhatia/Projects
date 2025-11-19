package com.fittracker.workout.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkoutExerciseRequest {

    @NotNull(message = "Exercise ID is required")
    private Long exerciseId;

    @Min(value = 1, message = "Planned sets must be at least 1")
    private Integer plannedSets;

    @Min(value = 1, message = "Planned reps must be at least 1")
    private Integer plannedReps;

    private Integer plannedDurationSeconds;

    private Integer actualSets;

    private Integer actualReps;

    private Integer actualDurationSeconds;

    private BigDecimal weightKg;

    private String notes;
}
