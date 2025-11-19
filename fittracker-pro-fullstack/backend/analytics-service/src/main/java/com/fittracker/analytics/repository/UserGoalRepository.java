package com.fittracker.analytics.repository;

import com.fittracker.analytics.entity.UserGoal;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface UserGoalRepository extends JpaRepository<UserGoal, Long> {

    List<UserGoal> findByUserIdAndStatus(Long userId, UserGoal.GoalStatus status);

    List<UserGoal> findByUserIdOrderByCreatedAtDesc(Long userId);

    List<UserGoal> findByUserIdAndGoalType(Long userId, UserGoal.GoalType goalType);

    @Query("SELECT g FROM UserGoal g WHERE g.userId = :userId " +
           "AND g.targetDate BETWEEN :startDate AND :endDate")
    List<UserGoal> findGoalsDueInPeriod(@Param("userId") Long userId,
                                       @Param("startDate") LocalDate startDate,
                                       @Param("endDate") LocalDate endDate);

    @Query("SELECT COUNT(g) FROM UserGoal g WHERE g.userId = :userId " +
           "AND g.status = 'COMPLETED' " +
           "AND g.completedAt BETWEEN :startDate AND :endDate")
    Long countGoalsCompletedInPeriod(@Param("userId") Long userId,
                                     @Param("startDate") LocalDate startDate,
                                     @Param("endDate") LocalDate endDate);

    @Query("SELECT g FROM UserGoal g WHERE g.userId = :userId " +
           "AND g.status = 'ACTIVE' AND g.targetDate < :date")
    List<UserGoal> findOverdueGoals(@Param("userId") Long userId, @Param("date") LocalDate date);
}
