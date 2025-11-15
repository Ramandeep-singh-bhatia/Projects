package com.interviewtracker.repository;

import com.interviewtracker.model.MockInterview;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface MockInterviewRepository extends JpaRepository<MockInterview, Long> {

    List<MockInterview> findByCompletedTrueOrderByStartTimeDesc();

    @Query("SELECT m FROM MockInterview m WHERE m.completed = false ORDER BY m.startTime DESC")
    Optional<MockInterview> findActiveInterview();

    @Query("SELECT m FROM MockInterview m WHERE m.completed = true AND m.startTime >= :startDate ORDER BY m.startTime DESC")
    List<MockInterview> findCompletedAfter(@Param("startDate") LocalDateTime startDate);

    @Query("SELECT m FROM MockInterview m WHERE m.completed = true ORDER BY m.startTime DESC LIMIT :limit")
    List<MockInterview> findRecentCompleted(@Param("limit") int limit);

    @Query("SELECT AVG(m.overallPerformance) FROM MockInterview m WHERE m.completed = true AND m.startTime >= :startDate")
    Double getAveragePerformanceAfter(@Param("startDate") LocalDateTime startDate);
}
