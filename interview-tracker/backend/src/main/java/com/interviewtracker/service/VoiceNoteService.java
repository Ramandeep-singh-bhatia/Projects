package com.interviewtracker.service;

import com.interviewtracker.model.Topic;
import com.interviewtracker.model.VoiceNote;
import com.interviewtracker.repository.TopicRepository;
import com.interviewtracker.repository.VoiceNoteRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class VoiceNoteService {

    private final VoiceNoteRepository voiceNoteRepository;
    private final TopicRepository topicRepository;

    private final String AUDIO_STORAGE_PATH = System.getProperty("user.home") + "/interview-tracker/audio";

    // Create voice note
    @Transactional
    public VoiceNote createVoiceNote(MultipartFile audioFile, VoiceNote voiceNote) throws IOException {
        // Create audio directory if it doesn't exist
        File audioDir = new File(AUDIO_STORAGE_PATH);
        if (!audioDir.exists()) {
            audioDir.mkdirs();
        }

        // Save audio file
        String fileName = voiceNote.getId() != null ? voiceNote.getId() + ".mp3" : UUID.randomUUID() + ".mp3";
        Path filePath = Paths.get(AUDIO_STORAGE_PATH, fileName);
        Files.write(filePath, audioFile.getBytes());

        voiceNote.setAudioFilePath(filePath.toString());
        voiceNote.setFileSize(audioFile.getSize());
        voiceNote.setRecordedDate(LocalDateTime.now());

        return voiceNoteRepository.save(voiceNote);
    }

    // Get voice note by ID
    public VoiceNote getVoiceNoteById(Long id) {
        return voiceNoteRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Voice note not found with id: " + id));
    }

    // Get all voice notes
    public List<VoiceNote> getAllVoiceNotes() {
        return voiceNoteRepository.findAll();
    }

    // Get voice notes by topic
    public List<VoiceNote> getVoiceNotesByTopic(Long topicId) {
        Topic topic = topicRepository.findById(topicId)
                .orElseThrow(() -> new RuntimeException("Topic not found with id: " + topicId));
        return voiceNoteRepository.findByTopicOrderByRecordedDateDesc(topic);
    }

    // Get recent voice notes
    public List<VoiceNote> getRecentVoiceNotes(int limit) {
        List<VoiceNote> all = voiceNoteRepository.findTop10ByOrderByRecordedDateDesc();
        return all.size() > limit ? all.subList(0, limit) : all;
    }

    // Update voice note
    @Transactional
    public VoiceNote updateVoiceNote(Long id, VoiceNote updatedVoiceNote) {
        VoiceNote existing = getVoiceNoteById(id);
        existing.setTitle(updatedVoiceNote.getTitle());
        existing.setSummary(updatedVoiceNote.getSummary());
        existing.setTranscription(updatedVoiceNote.getTranscription());
        existing.setTags(updatedVoiceNote.getTags());
        if (updatedVoiceNote.getTopic() != null) {
            existing.setTopic(updatedVoiceNote.getTopic());
        }
        if (updatedVoiceNote.getTranscription() != null && !updatedVoiceNote.getTranscription().isEmpty()) {
            existing.setTranscribed(true);
        }
        return voiceNoteRepository.save(existing);
    }

    // Delete voice note (and audio file)
    @Transactional
    public void deleteVoiceNote(Long id) throws IOException {
        VoiceNote voiceNote = getVoiceNoteById(id);

        // Delete audio file
        if (voiceNote.getAudioFilePath() != null) {
            Path filePath = Paths.get(voiceNote.getAudioFilePath());
            Files.deleteIfExists(filePath);
        }

        voiceNoteRepository.deleteById(id);
    }

    // Update transcription
    @Transactional
    public VoiceNote updateTranscription(Long id, String transcription) {
        VoiceNote voiceNote = getVoiceNoteById(id);
        voiceNote.setTranscription(transcription);
        voiceNote.setTranscribed(true);
        return voiceNoteRepository.save(voiceNote);
    }

    // Search voice notes by transcription
    public List<VoiceNote> searchVoiceNotes(String searchTerm) {
        return voiceNoteRepository.searchByTranscription(searchTerm);
    }

    // Get voice note statistics
    public Map<String, Object> getVoiceNoteStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalVoiceNotes", voiceNoteRepository.count());

        Long totalDuration = voiceNoteRepository.getTotalDuration();
        stats.put("totalDuration", totalDuration != null ? totalDuration : 0);

        Long totalSize = voiceNoteRepository.getTotalFileSize();
        stats.put("totalFileSize", totalSize != null ? totalSize : 0);

        List<VoiceNote> all = voiceNoteRepository.findAll();
        if (!all.isEmpty()) {
            double avgDuration = all.stream()
                    .filter(v -> v.getDuration() != null)
                    .mapToInt(VoiceNote::getDuration)
                    .average()
                    .orElse(0.0);
            stats.put("averageDuration", Math.round(avgDuration));
        } else {
            stats.put("averageDuration", 0);
        }

        long transcribedCount = voiceNoteRepository.findByTranscribedTrue().size();
        stats.put("transcribedCount", transcribedCount);

        return stats;
    }

    // Append transcription to topic notes
    @Transactional
    public void appendTranscriptionToTopicNotes(Long voiceNoteId) {
        VoiceNote voiceNote = getVoiceNoteById(voiceNoteId);
        if (voiceNote.getTopic() == null || voiceNote.getTranscription() == null) {
            throw new RuntimeException("Voice note must have both topic and transcription");
        }

        Topic topic = voiceNote.getTopic();
        String currentNotes = topic.getThingsToRemember() != null ? topic.getThingsToRemember() : "";
        String updatedNotes = currentNotes + "\n\n[Voice Note - " + voiceNote.getRecordedDate() + "]\n" + voiceNote.getTranscription();

        topic.setThingsToRemember(updatedNotes);
        topicRepository.save(topic);
    }
}
