package com.interviewtracker.controller;

import com.interviewtracker.dto.DashboardSuggestionDTO;
import com.interviewtracker.dto.WeeklyProgressDTO;
import com.interviewtracker.model.TopicCategory;
import com.interviewtracker.service.DashboardService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/dashboard")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class DashboardController {

    @Autowired
    private DashboardService dashboardService;

    @GetMapping("/suggestions")
    public ResponseEntity<List<DashboardSuggestionDTO>> getRevisionSuggestions(
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "15") int limit) {

        TopicCategory topicCategory = null;
        if (category != null && !category.isEmpty()) {
            topicCategory = TopicCategory.valueOf(category.toUpperCase());
        }

        List<DashboardSuggestionDTO> suggestions = dashboardService.getRevisionSuggestions(topicCategory, limit);
        return ResponseEntity.ok(suggestions);
    }

    @GetMapping("/weekly/progress")
    public ResponseEntity<WeeklyProgressDTO> getCurrentWeekProgress() {
        WeeklyProgressDTO progress = dashboardService.getCurrentWeekProgress();
        return ResponseEntity.ok(progress);
    }

    @GetMapping("/weekly/history")
    public ResponseEntity<List<WeeklyProgressDTO>> getWeeklyHistory(
            @RequestParam(defaultValue = "8") int weeks) {

        List<WeeklyProgressDTO> history = dashboardService.getWeeklyHistory(weeks);
        return ResponseEntity.ok(history);
    }
}
