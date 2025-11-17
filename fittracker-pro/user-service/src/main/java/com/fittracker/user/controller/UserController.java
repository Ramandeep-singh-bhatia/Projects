package com.fittracker.user.controller;

import com.fittracker.common.dto.ApiResponse;
import com.fittracker.user.dto.UserProfileDto;
import com.fittracker.user.dto.UserProfileRequest;
import com.fittracker.user.dto.WeightHistoryDto;
import com.fittracker.user.dto.WeightHistoryRequest;
import com.fittracker.user.service.UserProfileService;
import com.fittracker.user.service.WeightHistoryService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserProfileService profileService;
    private final WeightHistoryService weightHistoryService;

    @GetMapping("/profile")
    public ResponseEntity<ApiResponse<UserProfileDto>> getProfile(
            @RequestHeader("X-User-Id") String userId) {
        log.info("Get profile request for user: {}", userId);
        UserProfileDto profile = profileService.getProfile(Long.parseLong(userId));
        return ResponseEntity.ok(ApiResponse.success(profile));
    }

    @PutMapping("/profile")
    public ResponseEntity<ApiResponse<UserProfileDto>> updateProfile(
            @RequestHeader("X-User-Id") String userId,
            @Valid @RequestBody UserProfileRequest request) {
        log.info("Update profile request for user: {}", userId);
        UserProfileDto profile = profileService.createOrUpdateProfile(Long.parseLong(userId), request);
        return ResponseEntity.ok(ApiResponse.success("Profile updated successfully", profile));
    }

    @PostMapping("/weight")
    public ResponseEntity<ApiResponse<WeightHistoryDto>> logWeight(
            @RequestHeader("X-User-Id") String userId,
            @Valid @RequestBody WeightHistoryRequest request) {
        log.info("Log weight request for user: {}", userId);
        WeightHistoryDto weightHistory = weightHistoryService.logWeight(Long.parseLong(userId), request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Weight logged successfully", weightHistory));
    }

    @GetMapping("/weight/history")
    public ResponseEntity<ApiResponse<List<WeightHistoryDto>>> getWeightHistory(
            @RequestHeader("X-User-Id") String userId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        log.info("Get weight history request for user: {}", userId);

        List<WeightHistoryDto> history;
        if (startDate != null && endDate != null) {
            history = weightHistoryService.getWeightHistoryByDateRange(Long.parseLong(userId), startDate, endDate);
        } else {
            history = weightHistoryService.getWeightHistory(Long.parseLong(userId));
        }

        return ResponseEntity.ok(ApiResponse.success(history));
    }
}
