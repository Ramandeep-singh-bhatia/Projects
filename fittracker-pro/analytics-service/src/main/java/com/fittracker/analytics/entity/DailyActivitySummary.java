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
@Table(name = "daily_activity_summary")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DailyActivitySummary {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "activity_date", nullable = false)
    private LocalDate activityDate;

    @Column(name = "total_calories_consumed")
    private Integer totalCaloriesConsumed = 0;

    @Column(name = "total_calories_burned")
    private Integer totalCaloriesBurned = 0;

    @Column(name = "net_calories")
    private Integer netCalories = 0;

    @Column(name = "total_protein_g", precision = 8, scale = 2)
    private BigDecimal totalProteinG = BigDecimal.ZERO;

    @Column(name = "total_carbs_g", precision = 8, scale = 2)
    private BigDecimal totalCarbsG = BigDecimal.ZERO;

    @Column(name = "total_fat_g", precision = 8, scale = 2)
    private BigDecimal totalFatG = BigDecimal.ZERO;

    @Column(name = "meals_logged")
    private Integer mealsLogged = 0;

    @Column(name = "workouts_completed")
    private Integer workoutsCompleted = 0;

    @Column(name = "total_workout_duration_minutes")
    private Integer totalWorkoutDurationMinutes = 0;

    @Column(name = "active_minutes")
    private Integer activeMinutes = 0;

    @Column(name = "steps_count")
    private Integer stepsCount = 0;

    @Column(name = "water_intake_ml")
    private Integer waterIntakeMl = 0;

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

    /**
     * Calculate net calories (consumed - burned)
     */
    public void calculateNetCalories() {
        this.netCalories = (totalCaloriesConsumed != null ? totalCaloriesConsumed : 0) -
                          (totalCaloriesBurned != null ? totalCaloriesBurned : 0);
    }
}
