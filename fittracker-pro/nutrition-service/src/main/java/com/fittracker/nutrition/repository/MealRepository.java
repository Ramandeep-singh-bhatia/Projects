package com.fittracker.nutrition.repository;

import com.fittracker.nutrition.entity.Meal;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface MealRepository extends JpaRepository<Meal, Long> {

    List<Meal> findByUserIdAndMealDate(Long userId, LocalDate mealDate);

    List<Meal> findByUserIdAndMealDateBetweenOrderByMealDateDesc(Long userId, LocalDate startDate, LocalDate endDate);

    List<Meal> findByUserIdOrderByMealDateDescMealTimeDesc(Long userId);

    @Query("SELECT m FROM Meal m WHERE m.userId = :userId " +
           "AND m.mealDate >= :startDate ORDER BY m.mealDate DESC, m.mealTime DESC")
    List<Meal> findRecentMeals(@Param("userId") Long userId, @Param("startDate") LocalDate startDate);

    @Query("SELECT SUM(m.totalCalories) FROM Meal m " +
           "WHERE m.userId = :userId AND m.mealDate = :date")
    Double getTotalCaloriesForDate(@Param("userId") Long userId, @Param("date") LocalDate date);
}
