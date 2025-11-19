package com.fittracker.nutrition.service;

import com.fittracker.common.event.MealCreatedEvent;
import com.fittracker.common.exception.ResourceNotFoundException;
import com.fittracker.nutrition.dto.CreateMealRequest;
import com.fittracker.nutrition.entity.FoodItem;
import com.fittracker.nutrition.entity.Meal;
import com.fittracker.nutrition.entity.MealItem;
import com.fittracker.nutrition.kafka.EventPublisher;
import com.fittracker.nutrition.repository.FoodItemRepository;
import com.fittracker.nutrition.repository.MealRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class MealService {

    private final MealRepository mealRepository;
    private final FoodItemRepository foodItemRepository;
    private final EventPublisher eventPublisher;

    @Transactional
    public Meal createMeal(CreateMealRequest request) {
        log.info("Creating meal for user {}: {} on {}",
                request.getUserId(), request.getMealType(), request.getMealDate());

        // Create meal
        Meal meal = Meal.builder()
                .userId(request.getUserId())
                .mealType(request.getMealType())
                .mealDate(request.getMealDate())
                .mealTime(request.getMealTime() != null ? request.getMealTime() : LocalTime.now())
                .notes(request.getNotes())
                .build();

        // Add meal items
        request.getItems().forEach(itemRequest -> {
            FoodItem foodItem = foodItemRepository.findById(itemRequest.getFoodItemId())
                    .orElseThrow(() -> new ResourceNotFoundException(
                            "Food item not found with id: " + itemRequest.getFoodItemId()));

            BigDecimal servings = itemRequest.getServings();

            MealItem mealItem = MealItem.builder()
                    .foodItem(foodItem)
                    .servings(servings)
                    .calories(foodItem.getCaloriesPerServing().multiply(servings))
                    .proteinG(foodItem.getProteinG().multiply(servings))
                    .carbsG(foodItem.getCarbsG().multiply(servings))
                    .fatG(foodItem.getFatG().multiply(servings))
                    .fiberG(foodItem.getFiberG() != null ? foodItem.getFiberG().multiply(servings) : null)
                    .build();

            meal.addMealItem(mealItem);
        });

        Meal savedMeal = mealRepository.save(meal);
        log.info("Meal created with ID {}: {} calories", savedMeal.getId(), savedMeal.getTotalCalories());

        // Publish MealCreatedEvent
        MealCreatedEvent event = MealCreatedEvent.create(
                savedMeal.getId(),
                savedMeal.getUserId(),
                savedMeal.getMealType().name(),
                savedMeal.getMealDate(),
                savedMeal.getTotalCalories().intValue(),
                savedMeal.getTotalProteinG(),
                savedMeal.getTotalCarbsG(),
                savedMeal.getTotalFatG()
        );
        eventPublisher.publishMealCreatedEvent(event);

        return savedMeal;
    }

    @Transactional(readOnly = true)
    public Meal getMealById(Long mealId) {
        return mealRepository.findById(mealId)
                .orElseThrow(() -> new ResourceNotFoundException("Meal not found with id: " + mealId));
    }

    @Transactional(readOnly = true)
    public List<Meal> getUserMeals(Long userId) {
        return mealRepository.findByUserIdOrderByMealDateDescMealTimeDesc(userId);
    }

    @Transactional(readOnly = true)
    public List<Meal> getMealsForDate(Long userId, LocalDate date) {
        return mealRepository.findByUserIdAndMealDate(userId, date);
    }

    @Transactional(readOnly = true)
    public List<Meal> getMealsInRange(Long userId, LocalDate startDate, LocalDate endDate) {
        return mealRepository.findByUserIdAndMealDateBetweenOrderByMealDateDesc(userId, startDate, endDate);
    }

    @Transactional(readOnly = true)
    public List<Meal> getRecentMeals(Long userId, int days) {
        LocalDate startDate = LocalDate.now().minusDays(days);
        return mealRepository.findRecentMeals(userId, startDate);
    }

    @Transactional
    public void deleteMeal(Long mealId) {
        Meal meal = getMealById(mealId);
        log.info("Deleting meal {}", mealId);
        mealRepository.delete(meal);
    }

    @Transactional(readOnly = true)
    public Double getTotalCaloriesForDate(Long userId, LocalDate date) {
        Double total = mealRepository.getTotalCaloriesForDate(userId, date);
        return total != null ? total : 0.0;
    }
}
