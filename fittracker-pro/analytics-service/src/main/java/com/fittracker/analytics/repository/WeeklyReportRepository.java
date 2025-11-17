package com.fittracker.analytics.repository;

import com.fittracker.analytics.entity.WeeklyReport;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface WeeklyReportRepository extends JpaRepository<WeeklyReport, Long> {

    Optional<WeeklyReport> findByUserIdAndWeekStartDate(Long userId, LocalDate weekStartDate);

    List<WeeklyReport> findByUserIdOrderByWeekStartDateDesc(Long userId);

    @Query("SELECT w FROM WeeklyReport w WHERE w.userId = :userId " +
           "AND w.weekStartDate >= :startDate ORDER BY w.weekStartDate DESC")
    List<WeeklyReport> findRecentReports(@Param("userId") Long userId,
                                        @Param("startDate") LocalDate startDate);

    @Query("SELECT w FROM WeeklyReport w WHERE w.userId = :userId " +
           "ORDER BY w.consistencyScore DESC")
    List<WeeklyReport> findTopWeeksByConsistency(@Param("userId") Long userId);
}
