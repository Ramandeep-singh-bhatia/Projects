package com.fittracker.workout.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CompleteWorkoutRequest {

    @NotNull(message = "End time is required")
    private LocalDateTime endTime;
}
