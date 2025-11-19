package com.fittracker.analytics.repository;

import com.fittracker.analytics.entity.DailyActivitySummary;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface DailyActivitySummaryRepository extends JpaRepository<DailyActivitySummary, Long> {

    Optional<DailyActivitySummary> findByUserIdAndActivityDate(Long userId, LocalDate activityDate);

    List<DailyActivitySummary> findByUserIdAndActivityDateBetweenOrderByActivityDateDesc(
            Long userId, LocalDate startDate, LocalDate endDate);

    List<DailyActivitySummary> findByUserIdOrderByActivityDateDesc(Long userId);

    @Query("SELECT d FROM DailyActivitySummary d WHERE d.userId = :userId " +
           "AND d.activityDate >= :startDate ORDER BY d.activityDate DESC")
    List<DailyActivitySummary> findRecentActivity(@Param("userId") Long userId,
                                                  @Param("startDate") LocalDate startDate);

    @Query("SELECT AVG(d.totalCaloriesConsumed) FROM DailyActivitySummary d " +
           "WHERE d.userId = :userId AND d.activityDate BETWEEN :startDate AND :endDate")
    Double calculateAverageCaloriesConsumed(@Param("userId") Long userId,
                                           @Param("startDate") LocalDate startDate,
                                           @Param("endDate") LocalDate endDate);

    @Query("SELECT AVG(d.totalCaloriesBurned) FROM DailyActivitySummary d " +
           "WHERE d.userId = :userId AND d.activityDate BETWEEN :startDate AND :endDate")
    Double calculateAverageCaloriesBurned(@Param("userId") Long userId,
                                          @Param("startDate") LocalDate startDate,
                                          @Param("endDate") LocalDate endDate);

    @Query("SELECT COUNT(d) FROM DailyActivitySummary d " +
           "WHERE d.userId = :userId AND d.activityDate BETWEEN :startDate AND :endDate " +
           "AND d.workoutsCompleted > 0")
    Long countDaysWithWorkouts(@Param("userId") Long userId,
                               @Param("startDate") LocalDate startDate,
                               @Param("endDate") LocalDate endDate);
}
