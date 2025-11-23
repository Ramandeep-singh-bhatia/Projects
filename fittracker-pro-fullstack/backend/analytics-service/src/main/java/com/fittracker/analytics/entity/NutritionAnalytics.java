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
@Table(name = "nutrition_analytics")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NutritionAnalytics {

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

    @Column(name = "avg_daily_calories", precision = 8, scale = 2)
    private BigDecimal avgDailyCalories = BigDecimal.ZERO;

    @Column(name = "avg_protein_g", precision = 8, scale = 2)
    private BigDecimal avgProteinG = BigDecimal.ZERO;

    @Column(name = "avg_carbs_g", precision = 8, scale = 2)
    private BigDecimal avgCarbsG = BigDecimal.ZERO;

    @Column(name = "avg_fat_g", precision = 8, scale = 2)
    private BigDecimal avgFatG = BigDecimal.ZERO;

    @Column(name = "total_meals_logged")
    private Integer totalMealsLogged = 0;

    @Column(name = "days_logged")
    private Integer daysLogged = 0;

    @Column(name = "adherence_percentage", precision = 5, scale = 2)
    private BigDecimal adherencePercentage = BigDecimal.ZERO;

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
