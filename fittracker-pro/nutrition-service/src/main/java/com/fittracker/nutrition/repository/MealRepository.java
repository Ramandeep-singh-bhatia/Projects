package com.fittracker.nutrition.repository;

import com.fittracker.nutrition.entity.Meal;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface MealRepository extends JpaRepository<Meal, Long> {

    List<Meal> findByUserIdAndMealDate(Long userId, LocalDate mealDate);

    List<Meal> findByUserIdAndMealDateBetweenOrderByMealDateDesc(Long userId, LocalDate startDate, LocalDate endDate);
}
