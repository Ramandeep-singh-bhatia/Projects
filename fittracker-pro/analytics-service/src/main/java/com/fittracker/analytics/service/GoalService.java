package com.fittracker.analytics.service;

import com.fittracker.analytics.entity.GoalProgressTracking;
import com.fittracker.analytics.entity.UserGoal;
import com.fittracker.analytics.repository.UserGoalRepository;
import com.fittracker.common.exception.BadRequestException;
import com.fittracker.common.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class GoalService {

    private final UserGoalRepository userGoalRepository;

    /**
     * Create a new goal for a user
     */
    @Transactional
    public UserGoal createGoal(Long userId, UserGoal.GoalType goalType, BigDecimal targetValue,
                               String unit, LocalDate targetDate, String description) {
        UserGoal goal = UserGoal.builder()
                .userId(userId)
                .goalType(goalType)
                .targetValue(targetValue)
                .currentValue(BigDecimal.ZERO)
                .unit(unit)
                .startDate(LocalDate.now())
                .targetDate(targetDate)
                .status(UserGoal.GoalStatus.ACTIVE)
                .description(description)
                .build();

        log.info("Creating new goal for user {}: {} - target: {} {}",
                userId, goalType, targetValue, unit);
        return userGoalRepository.save(goal);
    }

    /**
     * Update goal progress
     */
    @Transactional
    public UserGoal updateGoalProgress(Long goalId, BigDecimal currentValue, String notes) {
        UserGoal goal = userGoalRepository.findById(goalId)
                .orElseThrow(() -> new ResourceNotFoundException("Goal not found with id: " + goalId));

        goal.setCurrentValue(currentValue);
        goal.calculateProgress();
        goal.checkCompletion();

        // Add progress tracking entry
        GoalProgressTracking tracking = GoalProgressTracking.builder()
                .goal(goal)
                .recordedDate(LocalDate.now())
                .currentValue(currentValue)
                .progressPercentage(goal.getProgressPercentage())
                .notes(notes)
                .build();
        goal.getProgressTracking().add(tracking);

        log.info("Updated goal {} progress: {} -> {}%", goalId, currentValue, goal.getProgressPercentage());
        return userGoalRepository.save(goal);
    }

    /**
     * Get all goals for a user with a specific status
     */
    @Transactional(readOnly = true)
    public List<UserGoal> getUserGoalsByStatus(Long userId, UserGoal.GoalStatus status) {
        return userGoalRepository.findByUserIdAndStatus(userId, status);
    }

    /**
     * Get all active goals for a user
     */
    @Transactional(readOnly = true)
    public List<UserGoal> getActiveGoals(Long userId) {
        return userGoalRepository.findByUserIdAndStatus(userId, UserGoal.GoalStatus.ACTIVE);
    }

    /**
     * Get all goals for a user
     */
    @Transactional(readOnly = true)
    public List<UserGoal> getAllGoals(Long userId) {
        return userGoalRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    /**
     * Get goal by ID
     */
    @Transactional(readOnly = true)
    public UserGoal getGoalById(Long goalId) {
        return userGoalRepository.findById(goalId)
                .orElseThrow(() -> new ResourceNotFoundException("Goal not found with id: " + goalId));
    }

    /**
     * Update goal status
     */
    @Transactional
    public UserGoal updateGoalStatus(Long goalId, UserGoal.GoalStatus newStatus) {
        UserGoal goal = getGoalById(goalId);

        if (goal.getStatus() == UserGoal.GoalStatus.COMPLETED) {
            throw new BadRequestException("Cannot change status of completed goal");
        }

        goal.setStatus(newStatus);

        if (newStatus == UserGoal.GoalStatus.COMPLETED) {
            goal.setCompletedAt(java.time.LocalDateTime.now());
        }

        log.info("Updated goal {} status to {}", goalId, newStatus);
        return userGoalRepository.save(goal);
    }

    /**
     * Delete a goal
     */
    @Transactional
    public void deleteGoal(Long goalId) {
        UserGoal goal = getGoalById(goalId);
        log.info("Deleting goal {}", goalId);
        userGoalRepository.delete(goal);
    }

    /**
     * Get goals due in a period
     */
    @Transactional(readOnly = true)
    public List<UserGoal> getGoalsDueInPeriod(Long userId, LocalDate startDate, LocalDate endDate) {
        return userGoalRepository.findGoalsDueInPeriod(userId, startDate, endDate);
    }

    /**
     * Get overdue goals
     */
    @Transactional(readOnly = true)
    public List<UserGoal> getOverdueGoals(Long userId) {
        return userGoalRepository.findOverdueGoals(userId, LocalDate.now());
    }

    /**
     * Count goals completed in a period
     */
    @Transactional(readOnly = true)
    public Long countGoalsCompletedInPeriod(Long userId, LocalDate startDate, LocalDate endDate) {
        return userGoalRepository.countGoalsCompletedInPeriod(userId, startDate, endDate);
    }
}
