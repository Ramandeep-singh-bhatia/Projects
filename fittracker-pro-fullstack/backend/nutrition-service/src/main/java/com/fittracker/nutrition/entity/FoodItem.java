package com.fittracker.nutrition.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "food_items")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FoodItem implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String brand;

    private String barcode;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private FoodCategory category;

    @Column(name = "serving_size", nullable = false, length = 100)
    private String servingSize;

    @Column(name = "serving_unit", nullable = false, length = 20)
    private String servingUnit;

    @Column(name = "calories_per_serving", nullable = false, precision = 8, scale = 2)
    private BigDecimal caloriesPerServing;

    @Column(name = "protein_g", nullable = false, precision = 6, scale = 2)
    @Builder.Default
    private BigDecimal proteinG = BigDecimal.ZERO;

    @Column(name = "carbs_g", nullable = false, precision = 6, scale = 2)
    @Builder.Default
    private BigDecimal carbsG = BigDecimal.ZERO;

    @Column(name = "fat_g", nullable = false, precision = 6, scale = 2)
    @Builder.Default
    private BigDecimal fatG = BigDecimal.ZERO;

    @Column(name = "fiber_g", precision = 6, scale = 2)
    private BigDecimal fiberG;

    @Column(name = "sugar_g", precision = 6, scale = 2)
    private BigDecimal sugarG;

    @Column(name = "sodium_mg", precision = 8, scale = 2)
    private BigDecimal sodiumMg;

    @Column(name = "cholesterol_mg", precision = 6, scale = 2)
    private BigDecimal cholesterolMg;

    @Column(name = "is_verified", nullable = false)
    @Builder.Default
    private Boolean isVerified = false;

    @Column(name = "created_by_user_id")
    private Long createdByUserId;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    public enum FoodCategory {
        FRUITS, VEGETABLES, GRAINS, PROTEIN, DAIRY,
        FATS_OILS, BEVERAGES, SNACKS, SWEETS, OTHER
    }
}
