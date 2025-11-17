package com.fittracker.analytics.repository;

import com.fittracker.analytics.entity.MonthlyReport;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface MonthlyReportRepository extends JpaRepository<MonthlyReport, Long> {

    Optional<MonthlyReport> findByUserIdAndYearAndMonth(Long userId, Integer year, Integer month);

    List<MonthlyReport> findByUserIdOrderByYearDescMonthDesc(Long userId);

    @Query("SELECT m FROM MonthlyReport m WHERE m.userId = :userId " +
           "AND (m.year > :year OR (m.year = :year AND m.month >= :month)) " +
           "ORDER BY m.year DESC, m.month DESC")
    List<MonthlyReport> findRecentReports(@Param("userId") Long userId,
                                         @Param("year") Integer year,
                                         @Param("month") Integer month);

    @Query("SELECT m FROM MonthlyReport m WHERE m.userId = :userId " +
           "ORDER BY m.totalWorkouts DESC")
    List<MonthlyReport> findTopMonthsByWorkouts(@Param("userId") Long userId);
}
