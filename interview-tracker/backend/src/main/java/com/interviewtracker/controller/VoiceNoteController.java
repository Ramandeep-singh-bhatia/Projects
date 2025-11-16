package com.interviewtracker.controller;

import com.interviewtracker.model.VoiceNote;
import com.interviewtracker.service.VoiceNoteService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/voice-notes")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class VoiceNoteController {

    private final VoiceNoteService voiceNoteService;

    // Create voice note (record and upload audio)
    @PostMapping("/record")
    public ResponseEntity<VoiceNote> createVoiceNote(
            @RequestParam("audio") MultipartFile audioFile,
            @RequestParam(required = false) Long topicId,
            @RequestParam(required = false) String title,
            @RequestParam(required = false) Integer duration) throws IOException {

        VoiceNote voiceNote = new VoiceNote();
        if (title != null) voiceNote.setTitle(title);
        if (duration != null) voiceNote.setDuration(duration);
        // Topic linking would be done via topicId

        VoiceNote created = voiceNoteService.createVoiceNote(audioFile, voiceNote);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    // Get voice note by ID
    @GetMapping("/{id}")
    public ResponseEntity<VoiceNote> getVoiceNoteById(@PathVariable Long id) {
        VoiceNote voiceNote = voiceNoteService.getVoiceNoteById(id);
        return ResponseEntity.ok(voiceNote);
    }

    // Get all voice notes
    @GetMapping
    public ResponseEntity<List<VoiceNote>> getAllVoiceNotes() {
        List<VoiceNote> voiceNotes = voiceNoteService.getAllVoiceNotes();
        return ResponseEntity.ok(voiceNotes);
    }

    // Get voice notes by topic
    @GetMapping("/topic/{topicId}")
    public ResponseEntity<List<VoiceNote>> getVoiceNotesByTopic(@PathVariable Long topicId) {
        List<VoiceNote> voiceNotes = voiceNoteService.getVoiceNotesByTopic(topicId);
        return ResponseEntity.ok(voiceNotes);
    }

    // Update voice note
    @PutMapping("/{id}")
    public ResponseEntity<VoiceNote> updateVoiceNote(@PathVariable Long id, @RequestBody VoiceNote voiceNote) {
        VoiceNote updated = voiceNoteService.updateVoiceNote(id, voiceNote);
        return ResponseEntity.ok(updated);
    }

    // Delete voice note
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteVoiceNote(@PathVariable Long id) throws IOException {
        voiceNoteService.deleteVoiceNote(id);
        return ResponseEntity.noContent().build();
    }

    // Download audio file
    @GetMapping("/{id}/audio")
    public ResponseEntity<Resource> downloadAudio(@PathVariable Long id) {
        VoiceNote voiceNote = voiceNoteService.getVoiceNoteById(id);
        Resource resource = new FileSystemResource(voiceNote.getAudioFilePath());

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("audio/mpeg"))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + voiceNote.getId() + ".mp3\"")
                .body(resource);
    }

    // Update transcription
    @PutMapping("/{id}/transcription")
    public ResponseEntity<VoiceNote> updateTranscription(@PathVariable Long id, @RequestBody Map<String, String> request) {
        String transcription = request.get("transcription");
        VoiceNote updated = voiceNoteService.updateTranscription(id, transcription);
        return ResponseEntity.ok(updated);
    }

    // Search voice notes
    @GetMapping("/search")
    public ResponseEntity<List<VoiceNote>> searchVoiceNotes(@RequestParam String q) {
        List<VoiceNote> results = voiceNoteService.searchVoiceNotes(q);
        return ResponseEntity.ok(results);
    }

    // Get voice note statistics
    @GetMapping("/analytics")
    public ResponseEntity<Map<String, Object>> getVoiceNoteStats() {
        Map<String, Object> stats = voiceNoteService.getVoiceNoteStats();
        return ResponseEntity.ok(stats);
    }

    // Append transcription to topic notes
    @PostMapping("/{id}/to-notes")
    public ResponseEntity<Void> appendToTopicNotes(@PathVariable Long id) {
        voiceNoteService.appendTranscriptionToTopicNotes(id);
        return ResponseEntity.ok().build();
    }
}
