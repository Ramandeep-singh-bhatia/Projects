package com.fittracker.analytics.repository;

import com.fittracker.analytics.entity.WorkoutAnalytics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface WorkoutAnalyticsRepository extends JpaRepository<WorkoutAnalytics, Long> {

    List<WorkoutAnalytics> findByUserIdAndPeriodTypeOrderByStartDateDesc(
            Long userId, WorkoutAnalytics.PeriodType periodType);

    Optional<WorkoutAnalytics> findByUserIdAndPeriodTypeAndStartDateAndEndDate(
            Long userId, WorkoutAnalytics.PeriodType periodType, LocalDate startDate, LocalDate endDate);

    @Query("SELECT w FROM WorkoutAnalytics w WHERE w.userId = :userId " +
           "AND w.periodType = :periodType AND w.startDate >= :since " +
           "ORDER BY w.startDate DESC")
    List<WorkoutAnalytics> findRecentAnalytics(@Param("userId") Long userId,
                                               @Param("periodType") WorkoutAnalytics.PeriodType periodType,
                                               @Param("since") LocalDate since);
}
