package com.interviewtracker.controller;

import com.interviewtracker.model.Flashcard;
import com.interviewtracker.service.FlashcardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/flashcards")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class FlashcardController {

    private final FlashcardService flashcardService;

    // Create flashcard
    @PostMapping
    public ResponseEntity<Flashcard> createFlashcard(@RequestBody Flashcard flashcard) {
        Flashcard created = flashcardService.createFlashcard(flashcard);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    // Get all flashcards
    @GetMapping
    public ResponseEntity<List<Flashcard>> getAllFlashcards(
            @RequestParam(required = false) Boolean activeOnly) {
        List<Flashcard> flashcards = activeOnly != null && activeOnly ?
                flashcardService.getActiveFlashcards() :
                flashcardService.getAllFlashcards();
        return ResponseEntity.ok(flashcards);
    }

    // Get flashcard by ID
    @GetMapping("/{id}")
    public ResponseEntity<Flashcard> getFlashcardById(@PathVariable Long id) {
        Flashcard flashcard = flashcardService.getFlashcardById(id);
        return ResponseEntity.ok(flashcard);
    }

    // Update flashcard
    @PutMapping("/{id}")
    public ResponseEntity<Flashcard> updateFlashcard(@PathVariable Long id, @RequestBody Flashcard flashcard) {
        Flashcard updated = flashcardService.updateFlashcard(id, flashcard);
        return ResponseEntity.ok(updated);
    }

    // Delete flashcard
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteFlashcard(@PathVariable Long id) {
        flashcardService.deleteFlashcard(id);
        return ResponseEntity.noContent().build();
    }

    // Archive flashcard
    @PostMapping("/{id}/archive")
    public ResponseEntity<Flashcard> archiveFlashcard(@PathVariable Long id) {
        Flashcard archived = flashcardService.archiveFlashcard(id);
        return ResponseEntity.ok(archived);
    }

    // Get flashcards due for review
    @GetMapping("/due")
    public ResponseEntity<List<Flashcard>> getFlashcardsDueForReview() {
        List<Flashcard> dueCards = flashcardService.getFlashcardsDueForReview();
        return ResponseEntity.ok(dueCards);
    }

    // Get next flashcard to review
    @GetMapping("/next")
    public ResponseEntity<Flashcard> getNextFlashcardToReview() {
        Flashcard next = flashcardService.getNextFlashcardToReview();
        if (next == null) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.ok(next);
    }

    // Submit flashcard review
    @PostMapping("/{id}/review")
    public ResponseEntity<Flashcard> submitReview(@PathVariable Long id, @RequestBody Map<String, Integer> request) {
        Integer quality = request.get("quality");
        if (quality == null) {
            return ResponseEntity.badRequest().build();
        }
        Flashcard reviewed = flashcardService.submitReview(id, quality);
        return ResponseEntity.ok(reviewed);
    }

    // Get flashcards by topic
    @GetMapping("/by-topic/{topicId}")
    public ResponseEntity<List<Flashcard>> getFlashcardsByTopic(@PathVariable Long topicId) {
        List<Flashcard> flashcards = flashcardService.getFlashcardsByTopic(topicId);
        return ResponseEntity.ok(flashcards);
    }

    // Get flashcards by category
    @GetMapping("/by-category")
    public ResponseEntity<List<Flashcard>> getFlashcardsByCategory(@RequestParam String category) {
        List<Flashcard> flashcards = flashcardService.getFlashcardsByCategory(category);
        return ResponseEntity.ok(flashcards);
    }

    // Search flashcards
    @GetMapping("/search")
    public ResponseEntity<List<Flashcard>> searchFlashcards(@RequestParam String q) {
        List<Flashcard> results = flashcardService.searchFlashcards(q);
        return ResponseEntity.ok(results);
    }

    // Get flashcard statistics
    @GetMapping("/analytics")
    public ResponseEntity<Map<String, Object>> getFlashcardStats() {
        Map<String, Object> stats = flashcardService.getFlashcardStats();
        return ResponseEntity.ok(stats);
    }

    // Auto-generate flashcards from topic
    @PostMapping("/generate/{topicId}")
    public ResponseEntity<List<Flashcard>> generateFlashcardsFromTopic(@PathVariable Long topicId) {
        List<Flashcard> generated = flashcardService.generateFlashcardsFromTopic(topicId);
        return ResponseEntity.ok(generated);
    }

    // Bulk create flashcards
    @PostMapping("/bulk-create")
    public ResponseEntity<List<Flashcard>> bulkCreateFlashcards(@RequestBody List<Flashcard> flashcards) {
        List<Flashcard> created = flashcardService.bulkCreateFlashcards(flashcards);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
}
