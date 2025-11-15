package com.interviewtracker.controller;

import com.interviewtracker.model.Topic;
import com.interviewtracker.service.DependencyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

@RestController
@RequestMapping("/api/dependencies")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class DependencyController {

    @Autowired
    private DependencyService dependencyService;

    @PostMapping("/topics/{topicId}/prerequisites/{prerequisiteId}")
    public ResponseEntity<Map<String, String>> addPrerequisite(
            @PathVariable Long topicId,
            @PathVariable Long prerequisiteId) {
        dependencyService.addPrerequisite(topicId, prerequisiteId);
        return ResponseEntity.ok(Map.of("message", "Prerequisite added successfully"));
    }

    @DeleteMapping("/topics/{topicId}/prerequisites/{prerequisiteId}")
    public ResponseEntity<Void> removePrerequisite(
            @PathVariable Long topicId,
            @PathVariable Long prerequisiteId) {
        dependencyService.removePrerequisite(topicId, prerequisiteId);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/topics/{topicId}/prerequisites")
    public ResponseEntity<Set<Topic>> getPrerequisites(@PathVariable Long topicId) {
        return ResponseEntity.ok(dependencyService.getPrerequisites(topicId));
    }

    @GetMapping("/topics/{topicId}/dependents")
    public ResponseEntity<Set<Topic>> getDependentTopics(@PathVariable Long topicId) {
        return ResponseEntity.ok(dependencyService.getDependentTopics(topicId));
    }

    @GetMapping("/topics/{topicId}/learning-path")
    public ResponseEntity<List<Map<String, Object>>> getLearningPath(@PathVariable Long topicId) {
        return ResponseEntity.ok(dependencyService.getLearningPath(topicId));
    }

    @GetMapping("/blocked")
    public ResponseEntity<List<Map<String, Object>>> getBlockedTopics() {
        return ResponseEntity.ok(dependencyService.getBlockedTopics());
    }

    @PostMapping("/validate")
    public ResponseEntity<Map<String, Boolean>> validateNonCircular(@RequestBody Map<String, Long> request) {
        boolean valid = dependencyService.validateNonCircular(
                request.get("topicId"),
                request.get("prerequisiteId")
        );
        return ResponseEntity.ok(Map.of("valid", valid));
    }

    @GetMapping("/ready-topics")
    public ResponseEntity<List<Topic>> getReadyTopics() {
        return ResponseEntity.ok(dependencyService.getReadyTopics());
    }

    @GetMapping("/next-logical-topic")
    public ResponseEntity<Optional<Topic>> getNextLogicalTopic() {
        return ResponseEntity.ok(dependencyService.getNextLogicalTopic());
    }

    @PostMapping("/import")
    public ResponseEntity<Map<String, String>> importPrerequisites(@RequestBody List<Map<String, Object>> data) {
        dependencyService.importPrerequisites(data);
        return ResponseEntity.ok(Map.of("message", "Prerequisites imported successfully"));
    }
}
