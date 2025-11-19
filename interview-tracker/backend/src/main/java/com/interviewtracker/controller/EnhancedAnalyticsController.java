package com.interviewtracker.controller;

import com.interviewtracker.dto.EnhancedAnalyticsDTO;
import com.interviewtracker.service.EnhancedAnalyticsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/analytics/enhanced")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class EnhancedAnalyticsController {

    @Autowired
    private EnhancedAnalyticsService enhancedAnalyticsService;

    @GetMapping
    public ResponseEntity<EnhancedAnalyticsDTO> getEnhancedAnalytics() {
        return ResponseEntity.ok(enhancedAnalyticsService.getEnhancedAnalytics());
    }
}
