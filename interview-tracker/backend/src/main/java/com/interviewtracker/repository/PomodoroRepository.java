package com.interviewtracker.repository;

import com.interviewtracker.model.Pomodoro;
import com.interviewtracker.model.PomodoroPhase;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface PomodoroRepository extends JpaRepository<Pomodoro, Long> {

    List<Pomodoro> findByTopicIdOrderByStartTimeDesc(Long topicId);

    @Query("SELECT p FROM Pomodoro p WHERE p.endTime IS NULL ORDER BY p.startTime DESC")
    Optional<Pomodoro> findActivePomodoro();

    @Query("SELECT p FROM Pomodoro p WHERE p.completed = true AND p.phase = :phase AND p.startTime >= :startDate")
    List<Pomodoro> findCompletedByPhaseAfter(@Param("phase") PomodoroPhase phase, @Param("startDate") LocalDateTime startDate);

    @Query("SELECT COUNT(p) FROM Pomodoro p WHERE p.completed = true AND p.phase = 'WORK' AND p.startTime >= :startDate")
    Long countCompletedWorkPomodorosAfter(@Param("startDate") LocalDateTime startDate);

    @Query("SELECT p FROM Pomodoro p WHERE p.completed = true ORDER BY p.startTime DESC LIMIT :limit")
    List<Pomodoro> findRecentCompleted(@Param("limit") int limit);
}
