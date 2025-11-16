package com.interviewtracker.controller;

import com.interviewtracker.model.CalibrationCheck;
import com.interviewtracker.model.CalibrationType;
import com.interviewtracker.model.Topic;
import com.interviewtracker.service.CalibrationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/calibration")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CalibrationController {

    private final CalibrationService calibrationService;

    // Get topics needing calibration
    @GetMapping("/pending-topics")
    public ResponseEntity<List<Topic>> getTopicsNeedingCalibration() {
        List<Topic> topics = calibrationService.getTopicsNeedingCalibration();
        return ResponseEntity.ok(topics);
    }

    // Trigger calibration for a topic
    @PostMapping("/trigger/{topicId}")
    public ResponseEntity<CalibrationCheck> triggerCalibration(
            @PathVariable Long topicId,
            @RequestParam CalibrationType type) {
        CalibrationCheck check = calibrationService.triggerCalibration(topicId, type);
        return ResponseEntity.status(HttpStatus.CREATED).body(check);
    }

    // Complete calibration check
    @PostMapping("/{id}/complete")
    public ResponseEntity<CalibrationCheck> completeCalibration(
            @PathVariable Long id,
            @RequestBody Map<String, Object> request) {
        Boolean passed = (Boolean) request.get("passed");
        String userResponse = (String) request.get("userResponse");
        String notes = (String) request.get("notes");

        CalibrationCheck completed = calibrationService.completeCalibration(id, passed, userResponse, notes);
        return ResponseEntity.ok(completed);
    }

    // Get pending calibrations
    @GetMapping("/pending")
    public ResponseEntity<List<CalibrationCheck>> getPendingCalibrations() {
        List<CalibrationCheck> pending = calibrationService.getPendingCalibrations();
        return ResponseEntity.ok(pending);
    }

    // Get calibration history for topic
    @GetMapping("/history/{topicId}")
    public ResponseEntity<List<CalibrationCheck>> getCalibrationHistory(@PathVariable Long topicId) {
        List<CalibrationCheck> history = calibrationService.getCalibrationHistory(topicId);
        return ResponseEntity.ok(history);
    }

    // Get calibration accuracy metrics
    @GetMapping("/accuracy")
    public ResponseEntity<Map<String, Object>> getCalibrationAccuracy() {
        Map<String, Object> accuracy = calibrationService.getCalibrationAccuracy();
        return ResponseEntity.ok(accuracy);
    }
}
