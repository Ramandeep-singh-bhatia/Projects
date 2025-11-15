package com.interviewtracker.controller;

import com.interviewtracker.model.PracticeSession;
import com.interviewtracker.service.PracticeSessionService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/sessions")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class PracticeSessionController {

    @Autowired
    private PracticeSessionService sessionService;

    @GetMapping("/topic/{topicId}")
    public ResponseEntity<List<PracticeSession>> getSessionsByTopicId(@PathVariable Long topicId) {
        List<PracticeSession> sessions = sessionService.getSessionsByTopicId(topicId);
        return ResponseEntity.ok(sessions);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PracticeSession> getSessionById(@PathVariable Long id) {
        PracticeSession session = sessionService.getSessionById(id);
        return ResponseEntity.ok(session);
    }

    @PostMapping("/topic/{topicId}")
    public ResponseEntity<PracticeSession> createSession(
            @PathVariable Long topicId,
            @Valid @RequestBody PracticeSession session) {

        PracticeSession createdSession = sessionService.createSession(topicId, session);
        return new ResponseEntity<>(createdSession, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<PracticeSession> updateSession(
            @PathVariable Long id,
            @Valid @RequestBody PracticeSession session) {

        PracticeSession updatedSession = sessionService.updateSession(id, session);
        return ResponseEntity.ok(updatedSession);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSession(@PathVariable Long id) {
        sessionService.deleteSession(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/recent")
    public ResponseEntity<List<PracticeSession>> getRecentSessions(
            @RequestParam(defaultValue = "10") int limit) {

        List<PracticeSession> sessions = sessionService.getRecentSessions(limit);
        return ResponseEntity.ok(sessions);
    }
}
