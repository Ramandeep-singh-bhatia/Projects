package com.fittracker.common.event;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MealCreatedEvent implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long mealId;
    private Long userId;
    private String mealType; // BREAKFAST, LUNCH, DINNER, SNACK
    private LocalDate mealDate;
    private Integer totalCalories;
    private BigDecimal totalProteinG;
    private BigDecimal totalCarbsG;
    private BigDecimal totalFatG;
    private String eventId;
    private LocalDateTime eventTimestamp;

    public static MealCreatedEvent create(Long mealId, Long userId, String mealType, LocalDate mealDate,
                                         Integer totalCalories, BigDecimal totalProteinG,
                                         BigDecimal totalCarbsG, BigDecimal totalFatG) {
        return MealCreatedEvent.builder()
                .mealId(mealId)
                .userId(userId)
                .mealType(mealType)
                .mealDate(mealDate)
                .totalCalories(totalCalories)
                .totalProteinG(totalProteinG)
                .totalCarbsG(totalCarbsG)
                .totalFatG(totalFatG)
                .eventId(java.util.UUID.randomUUID().toString())
                .eventTimestamp(LocalDateTime.now())
                .build();
    }
}
