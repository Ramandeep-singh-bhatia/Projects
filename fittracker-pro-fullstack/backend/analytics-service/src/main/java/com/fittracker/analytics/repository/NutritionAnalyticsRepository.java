package com.fittracker.analytics.repository;

import com.fittracker.analytics.entity.NutritionAnalytics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface NutritionAnalyticsRepository extends JpaRepository<NutritionAnalytics, Long> {

    List<NutritionAnalytics> findByUserIdAndPeriodTypeOrderByStartDateDesc(
            Long userId, NutritionAnalytics.PeriodType periodType);

    Optional<NutritionAnalytics> findByUserIdAndPeriodTypeAndStartDateAndEndDate(
            Long userId, NutritionAnalytics.PeriodType periodType, LocalDate startDate, LocalDate endDate);

    @Query("SELECT n FROM NutritionAnalytics n WHERE n.userId = :userId " +
           "AND n.periodType = :periodType AND n.startDate >= :since " +
           "ORDER BY n.startDate DESC")
    List<NutritionAnalytics> findRecentAnalytics(@Param("userId") Long userId,
                                                 @Param("periodType") NutritionAnalytics.PeriodType periodType,
                                                 @Param("since") LocalDate since);
}
