package com.interviewtracker.controller;

import com.interviewtracker.model.MockInterview;
import com.interviewtracker.service.MockInterviewService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/mock-interview")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class MockInterviewController {

    @Autowired
    private MockInterviewService mockInterviewService;

    @PostMapping("/start")
    public ResponseEntity<Map<String, Object>> startInterview(@RequestBody Map<String, Object> request) {
        @SuppressWarnings("unchecked")
        List<String> categories = (List<String>) request.get("categories");
        String difficulty = (String) request.get("difficulty");
        Integer duration = (Integer) request.get("duration");
        String focusArea = (String) request.get("focusArea");

        Map<String, Object> result = mockInterviewService.startMockInterview(
                categories, difficulty, duration, focusArea
        );

        return new ResponseEntity<>(result, HttpStatus.CREATED);
    }

    @PostMapping("/{id}/complete")
    public ResponseEntity<MockInterview> completeInterview(
            @PathVariable Long id,
            @RequestBody Map<String, Object> request) {
        Integer overallPerformance = (Integer) request.get("overallPerformance");
        Integer overallConfidence = (Integer) request.get("overallConfidence");
        String generalNotes = (String) request.get("generalNotes");
        Integer pressureLevel = (Integer) request.get("pressureLevel");
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> questionAssessments = (List<Map<String, Object>>) request.get("questionAssessments");

        MockInterview completed = mockInterviewService.completeMockInterview(
                id, overallPerformance, overallConfidence, generalNotes, pressureLevel, questionAssessments
        );

        return ResponseEntity.ok(completed);
    }

    @GetMapping
    public ResponseEntity<List<MockInterview>> getAllInterviews() {
        return ResponseEntity.ok(mockInterviewService.getAllMockInterviews());
    }

    @GetMapping("/{id}")
    public ResponseEntity<MockInterview> getInterviewById(@PathVariable Long id) {
        return ResponseEntity.ok(mockInterviewService.getMockInterviewById(id));
    }

    @GetMapping("/analytics")
    public ResponseEntity<Map<String, Object>> getAnalytics() {
        return ResponseEntity.ok(mockInterviewService.getMockInterviewAnalytics());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteInterview(@PathVariable Long id) {
        mockInterviewService.deleteMockInterview(id);
        return ResponseEntity.noContent().build();
    }
}
