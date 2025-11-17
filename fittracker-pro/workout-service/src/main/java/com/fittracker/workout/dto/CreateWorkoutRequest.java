package com.fittracker.workout.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateWorkoutRequest {

    @NotNull(message = "User ID is required")
    private Long userId;

    @NotBlank(message = "Workout name is required")
    @Size(max = 255, message = "Workout name must not exceed 255 characters")
    private String workoutName;

    @NotNull(message = "Workout date is required")
    private LocalDate workoutDate;

    @NotNull(message = "Start time is required")
    private LocalDateTime startTime;

    @NotEmpty(message = "At least one exercise is required")
    @Valid
    private List<WorkoutExerciseRequest> exercises;

    @Size(max = 500, message = "Notes must not exceed 500 characters")
    private String notes;
}
