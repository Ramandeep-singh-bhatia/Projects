package com.fittracker.analytics.controller;

import com.fittracker.analytics.dto.CreateGoalRequest;
import com.fittracker.analytics.dto.UpdateGoalProgressRequest;
import com.fittracker.analytics.entity.UserGoal;
import com.fittracker.analytics.service.GoalService;
import com.fittracker.common.dto.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/analytics/goals")
@RequiredArgsConstructor
public class GoalController {

    private final GoalService goalService;

    @PostMapping
    public ResponseEntity<ApiResponse<UserGoal>> createGoal(@Valid @RequestBody CreateGoalRequest request) {
        log.info("Create goal request for user {}: {}", request.getUserId(), request.getGoalType());
        UserGoal goal = goalService.createGoal(
                request.getUserId(),
                request.getGoalType(),
                request.getTargetValue(),
                request.getUnit(),
                request.getTargetDate(),
                request.getDescription()
        );
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Goal created successfully", goal));
    }

    @PutMapping("/{goalId}/progress")
    public ResponseEntity<ApiResponse<UserGoal>> updateGoalProgress(
            @PathVariable Long goalId,
            @Valid @RequestBody UpdateGoalProgressRequest request) {
        log.info("Update goal {} progress: {}", goalId, request.getCurrentValue());
        UserGoal goal = goalService.updateGoalProgress(goalId, request.getCurrentValue(), request.getNotes());
        return ResponseEntity.ok(ApiResponse.success("Goal progress updated", goal));
    }

    @PutMapping("/{goalId}/status")
    public ResponseEntity<ApiResponse<UserGoal>> updateGoalStatus(
            @PathVariable Long goalId,
            @RequestParam UserGoal.GoalStatus status) {
        log.info("Update goal {} status to {}", goalId, status);
        UserGoal goal = goalService.updateGoalStatus(goalId, status);
        return ResponseEntity.ok(ApiResponse.success("Goal status updated", goal));
    }

    @GetMapping("/{goalId}")
    public ResponseEntity<ApiResponse<UserGoal>> getGoal(@PathVariable Long goalId) {
        log.info("Get goal by id: {}", goalId);
        UserGoal goal = goalService.getGoalById(goalId);
        return ResponseEntity.ok(ApiResponse.success(goal));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<ApiResponse<List<UserGoal>>> getAllGoals(@PathVariable Long userId) {
        log.info("Get all goals for user: {}", userId);
        List<UserGoal> goals = goalService.getAllGoals(userId);
        return ResponseEntity.ok(ApiResponse.success(goals));
    }

    @GetMapping("/user/{userId}/active")
    public ResponseEntity<ApiResponse<List<UserGoal>>> getActiveGoals(@PathVariable Long userId) {
        log.info("Get active goals for user: {}", userId);
        List<UserGoal> goals = goalService.getActiveGoals(userId);
        return ResponseEntity.ok(ApiResponse.success(goals));
    }

    @GetMapping("/user/{userId}/overdue")
    public ResponseEntity<ApiResponse<List<UserGoal>>> getOverdueGoals(@PathVariable Long userId) {
        log.info("Get overdue goals for user: {}", userId);
        List<UserGoal> goals = goalService.getOverdueGoals(userId);
        return ResponseEntity.ok(ApiResponse.success(goals));
    }

    @DeleteMapping("/{goalId}")
    public ResponseEntity<ApiResponse<Void>> deleteGoal(@PathVariable Long goalId) {
        log.info("Delete goal: {}", goalId);
        goalService.deleteGoal(goalId);
        return ResponseEntity.ok(ApiResponse.success("Goal deleted successfully", null));
    }
}
