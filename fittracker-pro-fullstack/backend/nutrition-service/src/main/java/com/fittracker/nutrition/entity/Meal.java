package com.fittracker.nutrition.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "meals")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Meal {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(name = "meal_type", nullable = false, length = 20)
    private MealType mealType;

    @Column(name = "meal_date", nullable = false)
    private LocalDate mealDate;

    @Column(name = "meal_time")
    private LocalTime mealTime;

    @Column(name = "total_calories", nullable = false, precision = 8, scale = 2)
    @Builder.Default
    private BigDecimal totalCalories = BigDecimal.ZERO;

    @Column(name = "total_protein_g", nullable = false, precision = 6, scale = 2)
    @Builder.Default
    private BigDecimal totalProteinG = BigDecimal.ZERO;

    @Column(name = "total_carbs_g", nullable = false, precision = 6, scale = 2)
    @Builder.Default
    private BigDecimal totalCarbsG = BigDecimal.ZERO;

    @Column(name = "total_fat_g", nullable = false, precision = 6, scale = 2)
    @Builder.Default
    private BigDecimal totalFatG = BigDecimal.ZERO;

    @Column(name = "total_fiber_g", precision = 6, scale = 2)
    private BigDecimal totalFiberG;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @OneToMany(mappedBy = "meal", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<MealItem> mealItems = new ArrayList<>();

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    public enum MealType {
        BREAKFAST, LUNCH, DINNER, SNACK
    }

    public void addMealItem(MealItem mealItem) {
        mealItems.add(mealItem);
        mealItem.setMeal(this);
        recalculateTotals();
    }

    public void removeMealItem(MealItem mealItem) {
        mealItems.remove(mealItem);
        mealItem.setMeal(null);
        recalculateTotals();
    }

    public void recalculateTotals() {
        this.totalCalories = mealItems.stream()
                .map(MealItem::getCalories)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        this.totalProteinG = mealItems.stream()
                .map(MealItem::getProteinG)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        this.totalCarbsG = mealItems.stream()
                .map(MealItem::getCarbsG)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        this.totalFatG = mealItems.stream()
                .map(MealItem::getFatG)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        this.totalFiberG = mealItems.stream()
                .map(MealItem::getFiberG)
                .filter(fiber -> fiber != null)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
