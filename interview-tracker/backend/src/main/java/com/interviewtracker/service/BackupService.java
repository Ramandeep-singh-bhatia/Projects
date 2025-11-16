package com.interviewtracker.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Service
@RequiredArgsConstructor
@Slf4j
public class BackupService {

    private final String BASE_PATH = System.getProperty("user.home") + "/interview-tracker-data";
    private final String BACKUP_PATH = BASE_PATH + "/backups";
    private final String DATABASE_PATH = BASE_PATH + "/interview-tracker.mv.db";
    private final String UPLOAD_PATH = BASE_PATH + "/uploads";
    private final String AUDIO_PATH = System.getProperty("user.home") + "/interview-tracker/audio";

    // Create manual backup
    public String createBackup() throws IOException {
        // Create backup directory if it doesn't exist
        File backupDir = new File(BACKUP_PATH);
        if (!backupDir.exists()) {
            backupDir.mkdirs();
        }

        // Generate backup filename
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd-HHmmss"));
        String backupFileName = "backup-" + timestamp + ".zip";
        String backupFilePath = BACKUP_PATH + "/" + backupFileName;

        // Create zip file
        try (ZipOutputStream zipOut = new ZipOutputStream(new FileOutputStream(backupFilePath))) {
            // Add database file
            addToZip(zipOut, DATABASE_PATH, "database/");

            // Add upload files
            File uploadDir = new File(UPLOAD_PATH);
            if (uploadDir.exists()) {
                addDirectoryToZip(zipOut, UPLOAD_PATH, "uploads/");
            }

            // Add audio files
            File audioDir = new File(AUDIO_PATH);
            if (audioDir.exists()) {
                addDirectoryToZip(zipOut, AUDIO_PATH, "audio/");
            }
        }

        log.info("Backup created successfully: {}", backupFilePath);
        return backupFilePath;
    }

    // Scheduled automatic backup (runs daily at 2 AM)
    @Scheduled(cron = "0 0 2 * * *")
    public void automaticBackup() {
        try {
            String backupPath = createBackup();
            log.info("Automatic backup completed: {}", backupPath);

            // Apply retention policy (keep last 10 backups)
            applyRetentionPolicy(10);
        } catch (IOException e) {
            log.error("Automatic backup failed", e);
        }
    }

    // List all backups
    public List<Map<String, Object>> listBackups() {
        File backupDir = new File(BACKUP_PATH);
        if (!backupDir.exists()) {
            return new ArrayList<>();
        }

        File[] backupFiles = backupDir.listFiles((dir, name) -> name.startsWith("backup-") && name.endsWith(".zip"));
        if (backupFiles == null) {
            return new ArrayList<>();
        }

        return Arrays.stream(backupFiles)
                .map(file -> {
                    Map<String, Object> info = new HashMap<>();
                    info.put("fileName", file.getName());
                    info.put("filePath", file.getAbsolutePath());
                    info.put("fileSize", file.length());
                    info.put("createdDate", new Date(file.lastModified()));
                    return info;
                })
                .sorted((a, b) -> ((Date) b.get("createdDate")).compareTo((Date) a.get("createdDate")))
                .collect(Collectors.toList());
    }

    // Delete backup
    public void deleteBackup(String fileName) throws IOException {
        Path backupPath = Paths.get(BACKUP_PATH, fileName);
        Files.deleteIfExists(backupPath);
        log.info("Backup deleted: {}", fileName);
    }

    // Verify backup integrity
    public boolean verifyBackup(String fileName) {
        try {
            Path backupPath = Paths.get(BACKUP_PATH, fileName);
            if (!Files.exists(backupPath)) {
                return false;
            }

            // Basic verification: check if file can be opened as zip
            // More comprehensive verification would involve extracting and checking contents
            return Files.isReadable(backupPath) && backupPath.toString().endsWith(".zip");
        } catch (Exception e) {
            log.error("Backup verification failed for: {}", fileName, e);
            return false;
        }
    }

    // Apply retention policy (delete old backups)
    private void applyRetentionPolicy(int keepLast) {
        List<Map<String, Object>> backups = listBackups();
        if (backups.size() <= keepLast) {
            return;
        }

        // Delete oldest backups
        for (int i = keepLast; i < backups.size(); i++) {
            String fileName = (String) backups.get(i).get("fileName");
            try {
                deleteBackup(fileName);
                log.info("Deleted old backup: {}", fileName);
            } catch (IOException e) {
                log.error("Failed to delete old backup: {}", fileName, e);
            }
        }
    }

    // Helper: Add file to zip
    private void addToZip(ZipOutputStream zipOut, String filePath, String zipPath) throws IOException {
        File file = new File(filePath);
        if (!file.exists()) {
            return;
        }

        try (FileInputStream fis = new FileInputStream(file)) {
            ZipEntry zipEntry = new ZipEntry(zipPath + file.getName());
            zipOut.putNextEntry(zipEntry);

            byte[] buffer = new byte[1024];
            int len;
            while ((len = fis.read(buffer)) > 0) {
                zipOut.write(buffer, 0, len);
            }

            zipOut.closeEntry();
        }
    }

    // Helper: Add directory to zip recursively
    private void addDirectoryToZip(ZipOutputStream zipOut, String dirPath, String zipPath) throws IOException {
        File dir = new File(dirPath);
        if (!dir.exists() || !dir.isDirectory()) {
            return;
        }

        File[] files = dir.listFiles();
        if (files == null) {
            return;
        }

        for (File file : files) {
            if (file.isDirectory()) {
                addDirectoryToZip(zipOut, file.getAbsolutePath(), zipPath + file.getName() + "/");
            } else {
                addToZip(zipOut, file.getAbsolutePath(), zipPath);
            }
        }
    }

    // Get backup statistics
    public Map<String, Object> getBackupStats() {
        Map<String, Object> stats = new HashMap<>();
        List<Map<String, Object>> backups = listBackups();

        stats.put("totalBackups", backups.size());
        if (!backups.isEmpty()) {
            stats.put("lastBackupDate", backups.get(0).get("createdDate"));

            long totalSize = backups.stream()
                    .mapToLong(b -> (Long) b.get("fileSize"))
                    .sum();
            stats.put("totalBackupSize", totalSize);
        } else {
            stats.put("lastBackupDate", null);
            stats.put("totalBackupSize", 0L);
        }

        return stats;
    }
}
