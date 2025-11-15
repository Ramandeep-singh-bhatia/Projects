package com.interviewtracker.controller;

import com.interviewtracker.model.StudyPlan;
import com.interviewtracker.service.StudyPlanService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/study-plan")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class StudyPlanController {

    @Autowired
    private StudyPlanService studyPlanService;

    @PostMapping("/generate")
    public ResponseEntity<StudyPlan> generatePlan(@RequestBody Map<String, Object> request) {
        LocalDate interviewDate = LocalDate.parse((String) request.get("interviewDate"));
        Integer daysAvailable = (Integer) request.get("daysAvailable");
        Integer hoursPerDay = (Integer) request.get("hoursPerDay");
        String priorityFocus = (String) request.get("priorityFocus");
        String topicSelection = (String) request.get("topicSelection");
        @SuppressWarnings("unchecked")
        List<Long> customTopicIds = (List<Long>) request.get("customTopicIds");

        StudyPlan plan = studyPlanService.generateStudyPlan(
                interviewDate, daysAvailable, hoursPerDay,
                priorityFocus, topicSelection, customTopicIds
        );

        return new ResponseEntity<>(plan, HttpStatus.CREATED);
    }

    @GetMapping("/active")
    public ResponseEntity<StudyPlan> getActivePlan() {
        StudyPlan plan = studyPlanService.getActivePlan();
        return plan != null ? ResponseEntity.ok(plan) : ResponseEntity.noContent().build();
    }

    @GetMapping
    public ResponseEntity<List<StudyPlan>> getAllPlans() {
        return ResponseEntity.ok(studyPlanService.getAllPlans());
    }

    @GetMapping("/{id}")
    public ResponseEntity<StudyPlan> getPlanById(@PathVariable Long id) {
        return ResponseEntity.ok(studyPlanService.getPlanById(id));
    }

    @PostMapping("/items/{itemId}/complete")
    public ResponseEntity<Map<String, String>> markItemComplete(
            @PathVariable Long itemId,
            @RequestBody Map<String, Integer> request) {
        studyPlanService.markItemComplete(itemId, request.get("actualMinutes"));
        return ResponseEntity.ok(Map.of("message", "Item marked complete"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePlan(@PathVariable Long id) {
        studyPlanService.deletePlan(id);
        return ResponseEntity.noContent().build();
    }
}
