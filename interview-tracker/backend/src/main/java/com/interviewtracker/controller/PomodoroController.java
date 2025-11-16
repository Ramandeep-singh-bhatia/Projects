package com.interviewtracker.controller;

import com.interviewtracker.model.Pomodoro;
import com.interviewtracker.model.PomodoroPhase;
import com.interviewtracker.service.PomodoroService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/pomodoro")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class PomodoroController {

    @Autowired
    private PomodoroService pomodoroService;

    @PostMapping("/start")
    public ResponseEntity<Pomodoro> startPomodoro(@RequestBody Map<String, Object> request) {
        Long topicId = request.get("topicId") != null ? ((Number) request.get("topicId")).longValue() : null;
        String phaseStr = (String) request.get("phase");
        PomodoroPhase phase = PomodoroPhase.valueOf(phaseStr);
        Integer pomodoroNumber = (Integer) request.get("pomodoroNumber");

        Pomodoro pomodoro = pomodoroService.startPomodoro(topicId, phase, pomodoroNumber);
        return new ResponseEntity<>(pomodoro, HttpStatus.CREATED);
    }

    @GetMapping("/active")
    public ResponseEntity<Pomodoro> getActive() {
        Optional<Pomodoro> active = pomodoroService.getActivePomodoro();
        return active.map(ResponseEntity::ok).orElse(ResponseEntity.noContent().build());
    }

    @PostMapping("/{id}/complete")
    public ResponseEntity<Pomodoro> complete(@PathVariable Long id) {
        Pomodoro pomodoro = pomodoroService.completePomodoro(id);
        return ResponseEntity.ok(pomodoro);
    }

    @PostMapping("/{id}/stop")
    public ResponseEntity<Pomodoro> stop(@PathVariable Long id) {
        Pomodoro pomodoro = pomodoroService.stopPomodoro(id);
        return ResponseEntity.ok(pomodoro);
    }

    @PostMapping("/{id}/log-session")
    public ResponseEntity<Pomodoro> logSession(
            @PathVariable Long id,
            @RequestBody Map<String, Object> request) {
        Integer performanceRating = (Integer) request.get("performanceRating");
        String quickNotes = (String) request.get("quickNotes");

        Pomodoro pomodoro = pomodoroService.logPomodoroSession(id, performanceRating, quickNotes);
        return ResponseEntity.ok(pomodoro);
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        return ResponseEntity.ok(pomodoroService.getPomodoroStatistics());
    }

    @GetMapping("/history")
    public ResponseEntity<List<Pomodoro>> getHistory(@RequestParam(defaultValue = "50") int limit) {
        return ResponseEntity.ok(pomodoroService.getPomodoroHistory(limit));
    }

    @GetMapping("/topic/{topicId}")
    public ResponseEntity<List<Pomodoro>> getByTopic(@PathVariable Long topicId) {
        return ResponseEntity.ok(pomodoroService.getPomodorosForTopic(topicId));
    }
}
