package com.interviewtracker.controller;

import com.interviewtracker.model.ConfidenceHistory;
import com.interviewtracker.service.ConfidenceDecayService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/confidence")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class ConfidenceDecayController {

    @Autowired
    private ConfidenceDecayService decayService;

    @PostMapping("/apply-decay")
    public ResponseEntity<Map<String, Object>> applyDecay() {
        int count = decayService.applyDecayManually();
        return ResponseEntity.ok(Map.of("message", "Decay applied", "topicsAffected", count));
    }

    @GetMapping("/history/{topicId}")
    public ResponseEntity<List<ConfidenceHistory>> getHistory(@PathVariable Long topicId) {
        return ResponseEntity.ok(decayService.getConfidenceHistory(topicId));
    }

    @GetMapping("/decay-preview")
    public ResponseEntity<List<Map<String, Object>>> getDecayPreview() {
        return ResponseEntity.ok(decayService.previewDecay());
    }
}
