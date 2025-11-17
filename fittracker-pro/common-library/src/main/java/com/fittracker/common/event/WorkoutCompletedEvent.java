package com.fittracker.common.event;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkoutCompletedEvent implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long workoutId;
    private Long userId;
    private LocalDate workoutDate;
    private Integer durationMinutes;
    private Integer caloriesBurned;
    private String workoutType; // STRENGTH, CARDIO, FLEXIBILITY, etc.
    private Integer exerciseCount;
    private String eventId;
    private LocalDateTime eventTimestamp;

    public static WorkoutCompletedEvent create(Long workoutId, Long userId, LocalDate workoutDate,
                                              Integer durationMinutes, Integer caloriesBurned,
                                              String workoutType, Integer exerciseCount) {
        return WorkoutCompletedEvent.builder()
                .workoutId(workoutId)
                .userId(userId)
                .workoutDate(workoutDate)
                .durationMinutes(durationMinutes)
                .caloriesBurned(caloriesBurned)
                .workoutType(workoutType)
                .exerciseCount(exerciseCount)
                .eventId(java.util.UUID.randomUUID().toString())
                .eventTimestamp(LocalDateTime.now())
                .build();
    }
}
