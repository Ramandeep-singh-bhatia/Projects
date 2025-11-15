package com.interviewtracker.controller;

import com.interviewtracker.dto.AnalyticsSummaryDTO;
import com.interviewtracker.model.PracticeSession;
import com.interviewtracker.service.AnalyticsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/analytics")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class AnalyticsController {

    @Autowired
    private AnalyticsService analyticsService;

    @GetMapping("/summary")
    public ResponseEntity<AnalyticsSummaryDTO> getAnalyticsSummary() {
        AnalyticsSummaryDTO summary = analyticsService.getAnalyticsSummary();
        return ResponseEntity.ok(summary);
    }

    @GetMapping("/recent-activity")
    public ResponseEntity<List<PracticeSession>> getRecentActivity(
            @RequestParam(defaultValue = "10") int limit) {

        List<PracticeSession> recentActivity = analyticsService.getRecentActivity(limit);
        return ResponseEntity.ok(recentActivity);
    }
}
