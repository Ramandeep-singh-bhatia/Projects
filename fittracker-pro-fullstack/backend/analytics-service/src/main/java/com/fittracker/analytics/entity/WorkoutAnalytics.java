package com.fittracker.analytics.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "workout_analytics")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkoutAnalytics {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;

    @Column(name = "end_date", nullable = false)
    private LocalDate endDate;

    @Enumerated(EnumType.STRING)
    @Column(name = "period_type", nullable = false, length = 20)
    private PeriodType periodType;

    @Column(name = "total_workouts")
    private Integer totalWorkouts = 0;

    @Column(name = "total_duration_minutes")
    private Integer totalDurationMinutes = 0;

    @Column(name = "total_calories_burned")
    private Integer totalCaloriesBurned = 0;

    @Column(name = "avg_workout_duration_minutes", precision = 8, scale = 2)
    private BigDecimal avgWorkoutDurationMinutes = BigDecimal.ZERO;

    @Column(name = "workout_frequency", precision = 5, scale = 2)
    private BigDecimal workoutFrequency = BigDecimal.ZERO;

    @Column(name = "most_common_workout_type", length = 50)
    private String mostCommonWorkoutType;

    @Column(name = "strength_workouts")
    private Integer strengthWorkouts = 0;

    @Column(name = "cardio_workouts")
    private Integer cardioWorkouts = 0;

    @Column(name = "flexibility_workouts")
    private Integer flexibilityWorkouts = 0;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    public enum PeriodType {
        DAILY,
        WEEKLY,
        MONTHLY
    }
}
