package com.interviewtracker.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.interviewtracker.config.FileStorageConfig;
import com.interviewtracker.exception.FileStorageException;
import com.interviewtracker.model.*;
import com.interviewtracker.repository.*;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
public class DataManagementService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private PracticeSessionRepository sessionRepository;

    @Autowired
    private FileMetadataRepository fileMetadataRepository;

    @Autowired
    private SettingsRepository settingsRepository;

    @Autowired
    private FileStorageConfig fileStorageConfig;

    private final ObjectMapper objectMapper;

    public DataManagementService() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());
        this.objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        this.objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
    }

    public Map<String, Object> exportData() {
        Map<String, Object> data = new HashMap<>();

        // Export all topics (will include sessions and file metadata through relationships)
        List<Topic> topics = topicRepository.findAll();
        data.put("topics", topics);

        // Export settings
        Settings settings = settingsRepository.findById(1L).orElse(null);
        data.put("settings", settings);

        // Export metadata
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("exportDate", LocalDateTime.now());
        metadata.put("version", "1.0.0");
        data.put("metadata", metadata);

        return data;
    }

    public String exportDataToJson() {
        try {
            Map<String, Object> data = exportData();
            return objectMapper.writeValueAsString(data);
        } catch (Exception e) {
            throw new FileStorageException("Failed to export data to JSON", e);
        }
    }

    @Transactional
    public void importData(Map<String, Object> data, boolean mergeWithExisting) {
        if (!mergeWithExisting) {
            // Clear existing data
            resetAllData(false); // Don't create backup again
        }

        try {
            // Import settings
            if (data.containsKey("settings") && data.get("settings") != null) {
                Settings settings = objectMapper.convertValue(data.get("settings"), Settings.class);
                settingsRepository.save(settings);
            }

            // Import topics (with sessions and files)
            if (data.containsKey("topics") && data.get("topics") != null) {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> topicMaps = (List<Map<String, Object>>) data.get("topics");

                for (Map<String, Object> topicMap : topicMaps) {
                    String category = (String) topicMap.get("category");
                    Topic topic;

                    switch (TopicCategory.valueOf(category)) {
                        case DSA -> topic = objectMapper.convertValue(topicMap, DSATopic.class);
                        case HLD -> topic = objectMapper.convertValue(topicMap, HLDTopic.class);
                        case LLD -> topic = objectMapper.convertValue(topicMap, LLDTopic.class);
                        case BEHAVIORAL -> topic = objectMapper.convertValue(topicMap, BehavioralTopic.class);
                        default -> throw new IllegalArgumentException("Unknown category: " + category);
                    }

                    // Clear IDs for new insert
                    topic.setId(null);
                    if (topic.getPracticeSessions() != null) {
                        topic.getPracticeSessions().forEach(s -> s.setId(null));
                    }
                    if (topic.getFiles() != null) {
                        topic.getFiles().forEach(f -> f.setId(null));
                    }

                    topicRepository.save(topic);
                }
            }
        } catch (Exception e) {
            throw new FileStorageException("Failed to import data", e);
        }
    }

    @Transactional
    public void resetAllData(boolean createBackup) {
        if (createBackup) {
            createBackup();
        }

        // Delete all data
        sessionRepository.deleteAll();
        fileMetadataRepository.deleteAll();
        topicRepository.deleteAll();

        // Reset settings to default
        Settings defaultSettings = new Settings();
        settingsRepository.save(defaultSettings);

        // Clean up uploaded files
        try {
            Path uploadPath = Paths.get(fileStorageConfig.getUploadDir());
            if (Files.exists(uploadPath)) {
                Files.walk(uploadPath)
                        .sorted(Comparator.reverseOrder())
                        .map(Path::toFile)
                        .forEach(File::delete);
                Files.createDirectories(uploadPath);
            }
        } catch (IOException e) {
            throw new FileStorageException("Failed to clean up uploaded files", e);
        }
    }

    public void createBackup() {
        try {
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss"));
            String backupFileName = "backup_" + timestamp + ".json";

            Path backupPath = Paths.get(fileStorageConfig.getBackupDir(), backupFileName);
            String jsonData = exportDataToJson();

            Files.writeString(backupPath, jsonData, StandardOpenOption.CREATE);

            System.out.println("Backup created: " + backupPath);
        } catch (IOException e) {
            throw new FileStorageException("Failed to create backup", e);
        }
    }

    public Map<String, Object> getStorageInfo() {
        Map<String, Object> info = new HashMap<>();

        // Database location
        info.put("databaseLocation", System.getProperty("user.home") + "/interview-tracker/data/tracker.mv.db");

        // Upload directory
        info.put("uploadDirectory", fileStorageConfig.getUploadDir());

        // Backup directory
        info.put("backupDirectory", fileStorageConfig.getBackupDir());

        // Calculate storage usage
        try {
            Path uploadPath = Paths.get(fileStorageConfig.getUploadDir());
            long uploadSize = Files.exists(uploadPath) ?
                    Files.walk(uploadPath)
                            .filter(Files::isRegularFile)
                            .mapToLong(p -> {
                                try {
                                    return Files.size(p);
                                } catch (IOException e) {
                                    return 0;
                                }
                            })
                            .sum() : 0;

            info.put("uploadStorageUsed", formatBytes(uploadSize));
            info.put("uploadStorageUsedBytes", uploadSize);
        } catch (IOException e) {
            info.put("uploadStorageUsed", "Unknown");
        }

        // Get last backup date
        try {
            Path backupPath = Paths.get(fileStorageConfig.getBackupDir());
            if (Files.exists(backupPath)) {
                Optional<Path> lastBackup = Files.list(backupPath)
                        .filter(p -> p.getFileName().toString().startsWith("backup_"))
                        .max(Comparator.comparing(p -> {
                            try {
                                return Files.getLastModifiedTime(p);
                            } catch (IOException e) {
                                return FileTime.fromMillis(0);
                            }
                        }));

                if (lastBackup.isPresent()) {
                    info.put("lastBackupDate", Files.getLastModifiedTime(lastBackup.get()).toString());
                    info.put("lastBackupFile", lastBackup.get().getFileName().toString());
                } else {
                    info.put("lastBackupDate", "Never");
                }
            } else {
                info.put("lastBackupDate", "Never");
            }
        } catch (IOException e) {
            info.put("lastBackupDate", "Unknown");
        }

        return info;
    }

    private String formatBytes(long bytes) {
        if (bytes < 1024) return bytes + " B";
        int exp = (int) (Math.log(bytes) / Math.log(1024));
        String pre = "KMGTPE".charAt(exp - 1) + "";
        return String.format("%.2f %sB", bytes / Math.pow(1024, exp), pre);
    }
}
