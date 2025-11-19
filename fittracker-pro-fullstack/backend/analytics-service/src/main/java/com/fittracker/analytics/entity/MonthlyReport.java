package com.fittracker.analytics.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "monthly_reports")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MonthlyReport {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "month", nullable = false)
    private Integer month;

    @Column(name = "year", nullable = false)
    private Integer year;

    @Column(name = "total_calories_consumed")
    private Integer totalCaloriesConsumed = 0;

    @Column(name = "total_calories_burned")
    private Integer totalCaloriesBurned = 0;

    @Column(name = "total_workouts")
    private Integer totalWorkouts = 0;

    @Column(name = "total_workout_minutes")
    private Integer totalWorkoutMinutes = 0;

    @Column(name = "avg_daily_calories", precision = 8, scale = 2)
    private BigDecimal avgDailyCalories = BigDecimal.ZERO;

    @Column(name = "weight_change_kg", precision = 5, scale = 2)
    private BigDecimal weightChangeKg = BigDecimal.ZERO;

    @Column(name = "goals_achieved")
    private Integer goalsAchieved = 0;

    @Column(name = "consistency_score", precision = 5, scale = 2)
    private BigDecimal consistencyScore = BigDecimal.ZERO;

    @Column(name = "best_week_start_date")
    private LocalDate bestWeekStartDate;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "report_data", columnDefinition = "jsonb")
    private Map<String, Object> reportData;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
